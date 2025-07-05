export default {
  async fetch(request, env, ctx) {
    const MYFEEDS = `
//profile-title: Free_Config
//profile-update-interval: 1
//subscription-userinfo: upload=0; download=0; total=10737418240000000; expire=2546249531

https://raw.githubusercontent.com/4n0nymou3/multi-proxy-config-fetcher/refs/heads/main/configs/proxy_configs.txt

https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/splitted/mixed

https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/splitted/channels

https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/splitted/subscribe
`;

    // جدا کردن هدرهای کامنت (خط‌هایی که با // شروع میشن)
    const headerLines = MYFEEDS
      .split('\n')
      .map(l => l.trim())
      .filter(l => l.startsWith('//'));

    // جدا کردن URL‌ها (خط‌هایی که با // شروع نمیشن و خالی نیستن)
    const urls = MYFEEDS
      .split('\n')
      .map(l => l.trim())
      .filter(l => l && !l.startsWith('//'));

    function deduplicate(lines) {
      const seen = new Set();
      const out = [];
      for (const line of lines) {
        if (!line.includes('://')) continue;
        const key = line.split('#')[0].toLowerCase();
        if (!seen.has(key)) {
          seen.add(key);
          out.push(line);
        }
      }
      return out;
    }

    function isBase64(str) {
      return /^[A-Za-z0-9+/= \r\n\t]+$/.test(str);
    }

    async function fetchAndParse(url) {
      try {
        const res = await fetch(url);
        if (!res.ok) return [];
        let text = await res.text();
        if (isBase64(text.trim())) {
          try {
            text = atob(text.trim());
          } catch {
            // ignore decode error
          }
        }
        const lines = text.split('\n').map(l => l.trim());
        return lines.filter(l => /^[a-zA-Z0-9\-]+:\/\//.test(l));
      } catch {
        return [];
      }
    }

    let allConfigs = [];
    for (const url of urls) {
      const configs = await fetchAndParse(url);
      allConfigs = allConfigs.concat(configs);
    }

    const uniqueConfigs = deduplicate(allConfigs);

    // اضافه کردن هدرهای کامنت بالا به خروجی
    const finalLines = [...headerLines, ...uniqueConfigs];

    const output = finalLines.join('\n');
    const encoded = btoa(output);

    return new Response(encoded, {
      status: 200,
      headers: {
        'Content-Type': 'text/plain; charset=utf-8',
        'Cache-Control': 'max-age=300',
        'Access-Control-Allow-Origin': '*',
      },
    });
  },
};
