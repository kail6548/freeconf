// ─── تنظیمات اصلی ───────────────────────────────────────────
const CONFIG = {
  // UUID مخفی — بدون این در URL کار نمی‌کنه
  UUID: "your-secret-uuid-here",          // ← تغییر بده

  // لیست سابسکریپشن‌ها
  SUBS: [
    "https://sub1.example.com/path",
    "https://sub2.example.com/path",
    "https://raw.githubusercontent.com/user/repo/main/sub.txt",
  ],

  FETCH_TIMEOUT: 8000,
  USER_AGENT: "ClashforWindows/0.20.39",
};

const SUPPORTED_PROTOCOLS = [
  "vless://", "trojan://", "ss://", "ssr://", "vmess://",
  "hysteria://", "hysteria2://", "hy2://", "tuic://",
  "wireguard://", "wg://", "reality://", "http://", "https://",
  "socks5://", "socks://", "naive+https://", "juicity://",
];

export default {
  async fetch(request) {
    const url = new URL(request.url);
    const pathParts = url.pathname.split("/").filter(Boolean);

    if (pathParts.length === 0 || pathParts[0] !== CONFIG.UUID) {
      return notFoundResponse();
    }

    const configs = await fetchAllSubs();

    // همیشه هم base64 هم raw رو برمیگردونه — کلاینت هر کدوم رو بخواد میگیره
    // ?raw=1 برای plain text، پیشفرض base64
    const raw = url.searchParams.get("raw") === "1";
    const body = raw ? configs.join("\n") : btoa(unescape(encodeURIComponent(configs.join("\n"))));

    return new Response(body, {
      headers: {
        "Content-Type": "text/plain; charset=utf-8",
        "Cache-Control": "no-store",
        "Subscription-Userinfo": "upload=0; download=0; total=10737418240000; expire=99999999999",
        "Profile-Update-Interval": "6",
        "Access-Control-Allow-Origin": "*",
      },
    });
  },
};

async function fetchAllSubs() {
  const results = await Promise.allSettled(
    CONFIG.SUBS.map((url) => fetchOneSub(url))
  );

  const all = [];
  for (const r of results) {
    if (r.status === "fulfilled" && r.value.length > 0) {
      all.push(...r.value);
    }
  }

  const unique = [...new Set(all)];

  return unique.filter((line) =>
    SUPPORTED_PROTOCOLS.some((p) => line.toLowerCase().startsWith(p))
  );
}

async function fetchOneSub(subUrl) {
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), CONFIG.FETCH_TIMEOUT);

    const res = await fetch(subUrl, {
      headers: { "User-Agent": CONFIG.USER_AGENT },
      signal: controller.signal,
    });
    clearTimeout(timer);

    if (!res.ok) return [];

    let text = (await res.text()).trim();

    // تلاش برای decode base64 — اگه نشد همون raw رو نگه میداره
    text = tryDecodeBase64(text);

    return text
      .split(/\r?\n/)
      .map((l) => l.trim())
      .filter((l) => l && !l.startsWith("#") && !l.startsWith("//"));
  } catch (e) {
    console.error(`Failed to fetch ${subUrl}:`, e.message);
    return [];
  }
}

function tryDecodeBase64(str) {
  // اگه کاراکترهای پروتکل داشت، احتمالاً raw هست
  if (SUPPORTED_PROTOCOLS.some((p) => str.includes(p))) return str;

  // تلاش برای base64 decode
  try {
    const decoded = decodeURIComponent(escape(atob(str.replace(/\s/g, ""))));
    // اگه بعد از decode یه پروتکل شناخته‌شده داشت، موفق بوده
    if (SUPPORTED_PROTOCOLS.some((p) => decoded.includes(p))) return decoded;
  } catch (_) {}

  return str;
}

function notFoundResponse() {
  return new Response(
    `<!DOCTYPE html><html><head><meta charset="UTF-8"><title>404</title>
<style>body{margin:0;display:flex;align-items:center;justify-content:center;
height:100vh;background:#0a0a0a;color:#333;font-family:monospace}</style>
</head><body><p>404 Not Found</p></body></html>`,
    { status: 404, headers: { "Content-Type": "text/html" } }
  );
}
