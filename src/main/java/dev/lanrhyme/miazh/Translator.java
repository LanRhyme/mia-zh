package dev.lanrhyme.miazh;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.text.MutableText;
import net.minecraft.text.Text;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * 离线词典翻译引擎。
 *
 * 服务端（Mine in Abyss）把物品名、lore、菜单标题等以字面文本组件下发，
 * 资源包的 lang 覆盖对这类文本无效，所以只能在客户端拦截组件并查表替换。
 */
public final class Translator {
    private static final String RESOURCE_DICT = "/mia-zh/dict.json";
    private static final String MISS = "\u0000";

    private static final Translator INSTANCE = new Translator();
    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().disableHtmlEscaping().create();

    public static Translator get() {
        return INSTANCE;
    }

    private Path dir;
    private Path dictFile;
    private Path userFile;
    private Path configFile;
    private Path harvestFile;

    private volatile boolean enabled = true;
    private volatile boolean harvest = true;
    private volatile Map<String, String> entries = Map.of();
    private volatile List<Pat> patterns = List.of();
    private volatile long dictStamp = -1L;
    private volatile long userStamp = -1L;
    private volatile long configStamp = -1L;

    private final Map<String, String> cache = new ConcurrentHashMap<>();
    private final Map<String, int[]> misses = new ConcurrentHashMap<>();
    private final Map<String, Integer> stats = new ConcurrentHashMap<>();
    private long lastHits = 0L;
    private long lastMisses = 0L;

    private Translator() {
    }

    // ---------------------------------------------------------------- 启动

    public void bootstrap() {
        try {
            dir = FabricLoader.getInstance().getConfigDir().resolve("mia-zh");
            Files.createDirectories(dir);
            dictFile = dir.resolve("dict.json");
            userFile = dir.resolve("user.json");
            configFile = dir.resolve("config.json");
            harvestFile = dir.resolve("harvest.txt");

            copyDefaultDict();
            load(true);
            startWatcher();
            MiaZhClient.LOG.info("[mia-zh] 就绪，词典目录 {}", dir);
        } catch (Throwable t) {
            MiaZhClient.LOG.error("[mia-zh] 初始化失败", t);
        }
    }

    /**
     * 释放 jar 内的默认词典。
     *
     * 用内容指纹判断，jar 里的词典一变就覆盖磁盘上的 dict.json，
     * 这样模组升级后新词条能立刻生效；用户自己的改动写在 user.json 里不受影响。
     */
    private void copyDefaultDict() throws IOException {
        Path marker = dir.resolve(".dict-rev");
        byte[] bundled;
        try (InputStream in = Translator.class.getResourceAsStream(RESOURCE_DICT)) {
            if (in == null) {
                MiaZhClient.LOG.warn("[mia-zh] jar 内缺少默认词典 " + RESOURCE_DICT);
                return;
            }
            bundled = in.readAllBytes();
        }
        String rev = Integer.toHexString(java.util.Arrays.hashCode(bundled));
        String known = Files.exists(marker) ? Files.readString(marker, StandardCharsets.UTF_8).strip() : "";
        if (rev.equals(known) && Files.exists(dictFile) && Files.size(dictFile) > 64) {
            return;
        }
        Files.write(dictFile, bundled);
        Files.writeString(marker, rev, StandardCharsets.UTF_8);
        MiaZhClient.LOG.info("[mia-zh] 已释放默认词典 ({}, {} KB)", rev, bundled.length / 1024);
    }

    // ---------------------------------------------------------------- 读盘

    private synchronized void load(boolean force) {
        try {
            long ds = Files.exists(dictFile) ? Files.getLastModifiedTime(dictFile).toMillis() : 0L;
            long us = Files.exists(userFile) ? Files.getLastModifiedTime(userFile).toMillis() : 0L;
            long cs = Files.exists(configFile) ? Files.getLastModifiedTime(configFile).toMillis() : 0L;
            if (!force && ds == dictStamp && us == userStamp && cs == configStamp) {
                return;
            }
            boolean first = dictStamp == -1L;
            dictStamp = ds;
            userStamp = us;
            configStamp = cs;

            Map<String, String> map = new HashMap<>();
            List<Pat> pats = new ArrayList<>();

            readInto(dictFile, map, pats);
            readInto(userFile, map, pats);   // 用户表后读，同名覆盖内置

            entries = Map.copyOf(map);
            patterns = List.copyOf(pats);
            cache.clear();
            MiaZhClient.LOG.info("[mia-zh] 词典载入: {} 条词条 / {} 条规则", map.size(), pats.size());
            if (first) {
                selfTest();
            }
        } catch (Throwable t) {
            MiaZhClient.LOG.error("[mia-zh] 词典读取失败", t);
        }
    }

    private void readInto(Path file, Map<String, String> map, List<Pat> pats) {
        if (file == null || !Files.exists(file)) {
            return;
        }
        try (BufferedReader r = Files.newBufferedReader(file, StandardCharsets.UTF_8)) {
            JsonObject root = JsonParser.parseReader(r).getAsJsonObject();
            if (root.has("enabled") && root.get("enabled").isJsonPrimitive()) {
                enabled = root.get("enabled").getAsBoolean();
            }
            if (root.has("harvest") && root.get("harvest").isJsonPrimitive()) {
                harvest = root.get("harvest").getAsBoolean();
            }
            JsonElement e = root.get("entries");
            if (e != null && e.isJsonObject()) {
                for (Map.Entry<String, JsonElement> en : e.getAsJsonObject().entrySet()) {
                    String k = en.getKey();
                    JsonElement v = en.getValue();
                    if (k == null || k.isEmpty() || v == null || !v.isJsonPrimitive()) {
                        continue;
                    }
                    String val = v.getAsString();
                    if (val == null || val.isEmpty()) {
                        continue;
                    }
                    map.put(k, val);
                }
            }
            JsonElement p = root.get("patterns");
            if (p != null && p.isJsonArray()) {
                JsonArray arr = p.getAsJsonArray();
                for (JsonElement pe : arr) {
                    if (pe == null || !pe.isJsonObject()) {
                        continue;
                    }
                    JsonObject po = pe.getAsJsonObject();
                    String rx = po.has("pattern") ? po.get("pattern").getAsString() : null;
                    String rep = po.has("replace") ? po.get("replace").getAsString() : null;
                    if (rx == null || rep == null || rx.isEmpty()) {
                        continue;
                    }
                    try {
                        pats.add(new Pat(Pattern.compile(rx), rep));
                    } catch (Throwable bad) {
                        MiaZhClient.LOG.warn("[mia-zh] 正则无效，已跳过: {}", rx);
                    }
                }
            }
        } catch (Throwable t) {
            MiaZhClient.LOG.error("[mia-zh] 无法解析 {}", file, t);
        }
    }

    /** 启动自检：确认词典和正则真的能出中文，方便从日志判断链路是否正常。 */
    private void selfTest() {
        String[][] probes = {
                {"Diamond Pickaxe", null},
                {"Cooked Cyatoria Drumstick", null},
                {"Corpse-Weeper Eye", null},
                {"Titanjaw Scale", null},
                {"Grade II Relic", null},
                {"It feels like it's staring into your soul...", null},
                {"Damage: 12", null},
        };
        int ok = 0;
        for (String[] probe : probes) {
            String out = lookup(probe[0]);
            probe[1] = out;
            if (out != null) {
                ok++;
            }
            MiaZhClient.LOG.info("[mia-zh] 自检 {} -> {}", probe[0], out == null ? "（未命中）" : out);
        }
        MiaZhClient.LOG.info("[mia-zh] 自检通过 {}/{}", ok, probes.length);
    }

    private void startWatcher() {
        Thread t = new Thread(() -> {
            long lastFlush = 0L;
            while (true) {
                try {
                    Thread.sleep(2000L);
                    load(false);
                    if (harvest && System.currentTimeMillis() - lastFlush > 20_000L) {
                        flushHarvest();
                        lastFlush = System.currentTimeMillis();
                    }
                    long h = stats.getOrDefault("hit", 0);
                    long m = stats.getOrDefault("miss", 0);
                    if (h != lastHits || m != lastMisses) {
                        lastHits = h;
                        lastMisses = m;
                        MiaZhClient.LOG.info("[mia-zh] 命中 {} 次 / 未命中 {} 次", h, m);
                    }
                } catch (InterruptedException ie) {
                    return;
                } catch (Throwable ignored) {
                    // 后台线程永远不炸
                }
            }
        }, "mia-zh-watcher");
        t.setDaemon(true);
        t.start();
    }

    // ---------------------------------------------------------------- 查表

    private String resolve(String raw) {
        if (raw == null) {
            return null;
        }
        String cached = cache.get(raw);
        if (cached != null) {
            return MISS.equals(cached) ? null : cached;
        }
        String out = lookup(raw);
        cache.put(raw, out == null ? MISS : out);
        if (cache.size() > 20000) {
            cache.clear();
        }
        return out;
    }

    private String lookup(String raw) {
        String direct = entries.get(raw);
        if (direct != null) {
            return direct;
        }
        String trimmed = raw.strip();
        if (!trimmed.equals(raw)) {
            direct = entries.get(trimmed);
            if (direct != null) {
                return direct;
            }
        }
        if (trimmed.isEmpty()) {
            return null;
        }
        // 带 § 颜色码的文本（服务端物品名常见），剥掉颜色码再查，命中后把首个颜色码带回去
        String clean = stripLegacyCodes(trimmed);
        if (!clean.equals(trimmed)) {
            direct = entries.get(clean);
            if (direct != null) {
                return leadingCodes(trimmed) + direct;
            }
        }
        for (Pat p : patterns) {
            try {
                Matcher m = p.pattern.matcher(clean);
                if (m.matches()) {
                    return m.replaceFirst(p.replace);
                }
            } catch (Throwable ignored) {
            }
        }
        return null;
    }

    /** §x 颜色码剥除 */
    private static String stripLegacyCodes(String s) {
        if (s.indexOf('\u00a7') < 0) {
            return s;
        }
        StringBuilder sb = new StringBuilder(s.length());
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c == '\u00a7' && i + 1 < s.length()) {
                i++;
                continue;
            }
            sb.append(c);
        }
        return sb.toString();
    }

    /** 取开头连续的 §x 颜色码，用于把颜色带回译文 */
    private static String leadingCodes(String s) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i + 1 < s.length(); i += 2) {
            if (s.charAt(i) == '\u00a7') {
                sb.append(s, i, i + 2);
            } else {
                break;
            }
        }
        return sb.toString();
    }

    /** 字体/前缀占位符（如 [mineinabyss:ui/prefixes/layer/layer_2@gui]、<emojy:layer_2>）原样放过 */
    private static boolean isOpaque(String s) {
        if (s.startsWith("[") && s.indexOf(':') > 0 && s.indexOf(']') > 0) {
            return true;
        }
        if (s.indexOf("<emojy:") >= 0 || s.indexOf("<prefix") >= 0) {
            return true;
        }
        return s.indexOf("@gui]") >= 0;
    }

    /** 记录没命中的原始英文，供后续人工翻译。 */
    private void recordMiss(String raw) {
        if (!harvest || raw == null || isOpaque(raw)) {
            return;
        }
        String s = stripLegacyCodes(raw).strip();
        if (s.length() < 2 || s.length() > 160) {
            return;
        }
        if (hasCjk(s)) {
            return;
        }
        int letters = 0;
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z')) {
                letters++;
            }
        }
        if (letters < 2) {
            return;
        }
        stats.merge("miss", 1, Integer::sum);
        int[] box = misses.computeIfAbsent(s, k -> new int[1]);
        synchronized (box) {
            box[0]++;
        }
    }

    private static boolean hasCjk(String s) {
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c >= 0x4E00 && c <= 0x9FFF) {
                return true;
            }
        }
        return false;
    }

    private void flushHarvest() {
        if (misses.isEmpty()) {
            return;
        }
        Map<String, int[]> snapshot = new HashMap<>(misses);
        misses.clear();
        StringBuilder sb = new StringBuilder();
        snapshot.entrySet().stream()
                .sorted((a, b) -> Integer.compare(b.getValue()[0], a.getValue()[0]))
                .forEach(en -> sb.append(en.getValue()[0]).append('\t').append(en.getKey()).append('\n'));
        try {
            if (Files.exists(harvestFile) && Files.size(harvestFile) > 2_000_000L) {
                Files.move(harvestFile, harvestFile.resolveSibling("harvest.old.txt"), StandardCopyOption.REPLACE_EXISTING);
            }
            Files.writeString(harvestFile, sb.toString(), StandardCharsets.UTF_8,
                    StandardOpenOption.CREATE, StandardOpenOption.APPEND);
        } catch (Throwable t) {
            MiaZhClient.LOG.warn("[mia-zh] 写 harvest 失败", t);
        }
    }

    // ---------------------------------------------------------------- 翻译

    public Text translate(Text in) {
        if (!enabled || in == null) {
            return in;
        }
        try {
            String whole = in.getString();
            if (whole == null || whole.isEmpty() || isOpaque(whole)) {
                return in;
            }
            String hit = resolve(whole);
            if (hit != null) {
                stats.merge("hit", 1, Integer::sum);
                return Text.literal(hit).setStyle(in.getStyle());
            }
            List<Text> siblings = in.getSiblings();
            if (siblings == null || siblings.isEmpty()) {
                recordMiss(whole);
                return in;
            }
            // 记录整行（不是碎片），方便翻译整句
            recordMiss(whole);

            Text[] mapped = new Text[siblings.size()];
            boolean changed = false;
            for (int i = 0; i < siblings.size(); i++) {
                Text sib = siblings.get(i);
                Text out = translate(sib);
                mapped[i] = out;
                if (out != sib) {
                    changed = true;
                }
            }
            if (!changed) {
                return in;
            }
            // 关键：新父节点必须带上原 style，否则子节点会丢掉继承来的 font / color
            MutableText out = MutableText.of(in.getContent());
            out.setStyle(in.getStyle());
            for (Text t : mapped) {
                out.append(t);
            }
            return out;
        } catch (Throwable t) {
            return in;
        }
    }

    public List<Text> translate(List<Text> lines) {
        if (!enabled || lines == null || lines.isEmpty()) {
            return lines;
        }
        try {
            List<Text> out = new ArrayList<>(lines.size());
            for (Text line : lines) {
                out.add(translate(line));
            }
            return out;
        } catch (Throwable t) {
            return lines;
        }
    }

    public Map<String, Integer> stats() {
        return Map.copyOf(stats);
    }

    public Path dir() {
        return dir;
    }

    private record Pat(Pattern pattern, String replace) {
    }
}
