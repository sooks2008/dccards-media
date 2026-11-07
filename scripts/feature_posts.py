"""DCCards feature-spotlight posts: Instagram carousel (1080x1350) + vertical video (1080x1920) per post.
Run: python3 scripts/feature_posts.py /path/to/DCCards-repo [post_key ...]
Uses the style helpers from the app repo's marketing/social/scripts/stock_radar.py.
"""
import os, sys, subprocess
from PIL import Image, ImageDraw

APP = os.path.abspath(sys.argv[1]); MEDIA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(APP); sys.path.insert(0, 'marketing/social/scripts')
import stock_radar as sr  # noqa: E402
from stock_radar import base, ctext, lines, pill, glowicon, framed, place, kicker_head, pop, lora, ease  # noqa: E402
GOLD, GREEN, TEXT, MUTED, BG = sr.GOLD, sr.GREEN, sr.TEXT, sr.MUTED, sr.BG

D = 'marketing/iphone_6.9in_1320x2868/'
def crop(f, box): return Image.open(D + f).convert('RGB').crop(box)

PICKER = crop('02_picker.png', (170, 1080, 1150, 2260))
DETAIL = crop('03_detail.png', (170, 740, 1150, 2760))
DETAIL_CARD = crop('03_detail.png', (170, 740, 1150, 2235))
DETAIL_VAULT = crop('03_detail.png', (170, 2285, 1150, 2760))
CHART = crop('04_stats.png', (170, 730, 1150, 1900))
WATCH = crop('04_stats.png', (170, 1930, 1150, 2470))
REW_TOP = crop('06_rewards.png', (170, 730, 1150, 1610))
REW_BOT = crop('06_rewards.png', (170, 1610, 1150, 2650))
VAULT = crop('01_vault.png', (170, 640, 1150, 2400))
VAULT_TOP = crop('01_vault.png', (170, 745, 1150, 1330))
MAP, STORE = sr.MAP, sr.STORE
VS = MEDIA + '/posts/2026-11-vault-social/instagram_carousel/'
FEED = Image.open(VS + '04_feed.png').convert('RGB').crop((184, 384, 896, 1279))
MARKET = Image.open(VS + '05_market.png').convert('RGB').crop((184, 384, 896, 1279))
CHAT = Image.open(VS + '06_chat.png').convert('RGB').crop((103, 384, 976, 1279))
CF = 'Sources/DCCCardTrackerCore/Resources/CardFronts/'
PINK = (220, 90, 170)


# ---------- slide builders ----------
def hook(W, H, top, big, sub, tag):
    c = base(W, H); d = ImageDraw.Draw(c); y = top
    glowicon(c, int(W * .2), (W - int(W * .2)) // 2, y); y += int(W * .2) + 80
    y = lines(d, W, y, big, lora(int(W * .105)), TEXT, 1.15) + 40
    y = lines(d, W, y, sub, lora(int(W * .055), 'Regular'), GOLD, 1.3) + 60
    pill(d, W, y, tag, pop(int(W * .034), 'Bold'), BG, GOLD)
    return c


def shot(W, H, top, kicker, head, ims, border=GOLD, note=None):
    c = base(W, H); y = kicker_head(c, W, top, kicker, head, int(W * .075)) + 50
    room = H - y - (190 if note else 80); gap = 36
    ims = ims if isinstance(ims, list) else [ims]
    # fit all crops in a column: width limited by both W*.84 and the available height
    tot = sum(i.height / i.width for i in ims)
    w = int(min(W * .84, (room - gap * (len(ims) - 1)) / tot))
    for i in ims:
        f = framed(i, w, border=border); place(c, f, (W - f.width) // 2, y); y += f.height + gap
    if note:
        lines(ImageDraw.Draw(c), W, y + 14, note, pop(int(W * .034), 'Regular'), MUTED, 1.5)
    return c


def cta(W, H, top, head, sub, kicker='NOW IN ALPHA', cta_text='Join the alpha at dccardsapp.com'):
    c = base(W, H); d = ImageDraw.Draw(c); y = top
    ctext(d, W, y, kicker, pop(int(W * .03)), GOLD, track=8); y += int(W * .03) + 50
    y = lines(d, W, y, head, lora(int(W * .085)), TEXT, 1.25) + 10
    y = lines(d, W, y, sub, lora(int(W * .045), 'Regular'), MUTED, 1.4) + 70
    sz = int(W * .2); glowicon(c, sz, (W - sz) // 2, y); y += sz + 80
    y = pill(d, W, y, cta_text, pop(int(W * .042), 'Bold'), BG, GOLD, 56, 26) + 40
    ctext(d, W, y, 'Link in bio', pop(int(W * .034)), TEXT); y += int(W * .034) + 90
    lines(d, W, y, ['iPhone now · Android coming soon', 'Fan-made, not affiliated with',
                    'Dungeon Crawler Carl or Matt Dinniman'], pop(int(W * .024), 'Regular'), MUTED, 1.6)
    return c


def textslide(W, H, top, kicker, head, body, pills):
    c = base(W, H); d = ImageDraw.Draw(c); y = kicker_head(c, W, top, kicker, head, int(W * .075)) + 60
    y = lines(d, W, y, body, pop(int(W * .036), 'Regular'), MUTED, 1.55) + 70
    for label, t in pills:
        ctext(d, W, y, label, pop(int(W * .028)), GOLD, track=6); y += int(W * .028) + 26
        y = pill(d, W, y, t, pop(int(W * .04), 'Bold'), BG, GOLD, 48, 22) + 70
    return c


def cardgrid(W, H, top, kicker, head, cards, note):
    """2x2 grid of numbered card fronts (cards: list of (file stem, name))."""
    c = base(W, H); d = ImageDraw.Draw(c); y = kicker_head(c, W, top, kicker, head, int(W * .075)) + 50
    gap = int(W * .05); cw = int(min((W * .86 - gap) / 2, ((H - y - 230) / 2 - 70) * 750 / 1050)); ch = int(cw * 1050 / 750)
    x0 = (W - 2 * cw - gap) // 2
    for i, (stem, name) in enumerate(cards):
        x = x0 + (i % 2) * (cw + gap); yy = y + (i // 2) * (ch + 90)
        im = Image.open(CF + stem + '.jpg').convert('RGB'); f = framed(im, cw, radius=24); place(c, f, x, yy)
        r = int(W * .035); d = ImageDraw.Draw(c)
        d.ellipse([x - r // 2, yy - r // 2, x + r * 3 // 2, yy + r * 3 // 2], fill=GOLD)
        nf = pop(int(r * 1.2), 'Bold'); n = str(i + 1); d.text((x + r // 2 - d.textlength(n, font=nf) / 2, yy + r // 2 - nf.size * .62), n, font=nf, fill=BG)
        ctext(d, cw, yy + ch + 14, name, pop(int(W * .03)), TEXT, x0=x)
    lines(ImageDraw.Draw(c), W, y + 2 * ch + 190, note, pop(int(W * .036), 'Regular'), MUTED, 1.5)
    return c


SUB = ['DCCards, the Dungeon Crawler Carl', 'card collection tracker.']

# Each post: list of (slide name, builder(W, H, portrait) -> image). portrait=True means the 1080x1920 video frame.
POSTS = {
    '2026-11-pull-odds': [
        ('01_hook', lambda W, H, v: hook(W, H, 420 if v else 140, ['1 in 7,200.'],
                                         ["That's the pull ratio on", 'a Sketch & Signed.'], 'DID YOU PULL ONE?')),
        ('02_versions', lambda W, H, v: shot(W, H, 220 if v else 80, 'VERSION TRACKING', ['Log exactly', 'which version you pulled'], PICKER)),
        ('03_copies', lambda W, H, v: shot(W, H, 220 if v else 80, 'EVERY COPY COUNTS', ['Classic, Emerald, Gold,', 'Rainbow, Sketch & Signed'],
                                           [DETAIL_CARD, DETAIL_VAULT] if v else DETAIL_VAULT,
                                           note=None if v else ['Every version you own, in one place,', 'with what each one sells for.'])),
        ('04_join_alpha', lambda W, H, v: cta(W, H, 380 if v else 130, ['Know what', 'you pulled.'], SUB)),
    ],
    '2026-11-price-check': [
        ('01_hook', lambda W, H, v: hook(W, H, 420 if v else 140, ["What's your", 'Princess Donut', 'worth?'],
                                         ['Stop guessing.'], 'REAL EBAY SOLD PRICES')),
        ('02_chart', lambda W, H, v: shot(W, H, 220 if v else 80, 'LIVE MARKET STATS', ['90 days of sold prices,', 'drag to see any day'], CHART, border=GREEN)),
        ('03_alerts', lambda W, H, v: shot(W, H, 220 if v else 90, 'PRICE ALERTS', ['Watch the cards', 'you want to buy or sell'], WATCH, border=GREEN,
                                          note=['Set a target price and get pinged', 'when the market hits it.'])),
        ('04_join_alpha', lambda W, H, v: cta(W, H, 380 if v else 130, ['Know what', "it's worth."], SUB)),
    ],
    '2026-11-system-ai': [
        ('01_hook', lambda W, H, v: hook(W, H, 420 if v else 140, ['The System AI', 'is watching', 'your collection.'],
                                         ['And it hands out loot boxes.'], 'ACHIEVEMENTS IN DCCARDS')),
        ('02_badge', lambda W, H, v: shot(W, H, 220 if v else 80, 'SYSTEM AI ACHIEVEMENTS', ['Hit milestones,', 'unlock profile badges'], REW_TOP)),
        ('03_boxes', lambda W, H, v: shot(W, H, 220 if v else 80, 'LOOT BOXES', ['Bronze, Silver, Gold.', 'Claim them all.'], REW_BOT)),
        ('04_join_alpha', lambda W, H, v: cta(W, H, 380 if v else 130, ['Earn it.', 'Then claim it.'], SUB)),
    ],
    '2026-11-best-pull': [
        ('01_hook', lambda W, H, v: hook(W, H, 420 if v else 140, ["What's the best", 'DCC card', "you've pulled?"],
                                         ['Drop it in the comments.'], 'SHOW US YOUR PULLS')),
        ('02_card', lambda W, H, v: shot(W, H, 220 if v else 80, 'RAREST ON DISPLAY', ['Your best pull,', 'always on top'], DETAIL_CARD)),
        ('03_vault', lambda W, H, v: shot(W, H, 220 if v else 80, 'YOUR VAULT', ['All 188 cards.', 'Every pull, tracked.'], VAULT)),
        ('04_join_alpha', lambda W, H, v: cta(W, H, 380 if v else 130, ['Show off', 'your pulls.'], SUB)),
    ],
    '2026-11-android': [
        ('01_hook', lambda W, H, v: hook(W, H, 420 if v else 140, ['Android', "crawlers, you're", 'next.'],
                                         ['DCCards is coming to Android.'], 'SAME APP · SAME VAULT')),
        ('02_crossplay', lambda W, H, v: shot(W, H, 220 if v else 80, 'IPHONE + ANDROID', ['One community.', 'Every crawler.'], FEED, border=PINK)),
        ('03_trade', lambda W, H, v: shot(W, H, 220 if v else 90, 'CROSS-PLATFORM', ['Chat, trade and sell', 'across iPhone and Android'], MARKET, border=PINK)),
        ('04_signup', lambda W, H, v: cta(W, H, 380 if v else 130, ['Android is', 'on the way.'], ['Sign up to hear the moment', 'it lands.'],
                                          kicker='COMING SOON', cta_text='Sign up at dccardsapp.com')),
    ],
    '2026-11-trading': [
        ('01_hook', lambda W, H, v: hook(W, H, 420 if v else 140, ['Trade with', 'crawlers.', 'Not scalpers.'],
                                         ['The DCCards Market is open.'], 'BUY · SELL · TRADE')),
        ('02_market', lambda W, H, v: shot(W, H, 220 if v else 80, 'THE MARKET', ['List your extras.', 'Find your missing cards.'], MARKET, border=PINK)),
        ('03_chat', lambda W, H, v: shot(W, H, 220 if v else 80, 'DIRECT MESSAGES', ['Make the deal', 'right in the app'], CHAT, border=PINK)),
        ('04_join_alpha', lambda W, H, v: cta(W, H, 380 if v else 130, ['Make the deal.'], SUB)),
    ],
    '2026-11-completion': [
        ('01_hook', lambda W, H, v: hook(W, H, 420 if v else 140, ['How many', 'of the 188', 'do you have?'],
                                         ['Be honest.'], 'COUNT YOUR VAULT')),
        ('02_progress', lambda W, H, v: shot(W, H, 220 if v else 90, 'SET PROGRESS', ['See exactly how close', 'you are to all 188'], VAULT_TOP,
                                             note=['Tap Unowned and you have', 'your hunt list. (Or your wishlist.)'])),
        ('03_vault', lambda W, H, v: shot(W, H, 220 if v else 80, 'YOUR VAULT', ['Every card you own,', 'every version, every value'], VAULT)),
        ('04_join_alpha', lambda W, H, v: cta(W, H, 380 if v else 130, ['Finish the set.'], SUB)),
    ],
    '2026-11-pick-one': [
        ('01_hook', lambda W, H, v: hook(W, H, 420 if v else 140, ['Pick one.'],
                                         ['Which DCC card would', 'you pull first?'], 'COMMENT 1, 2, 3 OR 4')),
        ('02_cards', lambda W, H, v: cardgrid(W, H, 220 if v else 70, 'PICK ONE', ['Which would you pull?'],
                                              [('DCC-S1-011', 'Princess Donut'), ('DCC-S1-016', 'Prepotente'),
                                               ('DCC-S1-041', 'Sluggalo'), ('DCC-S1-056', 'Clay-ton')], ['Drop your number in the comments.'])),
        ('03_join_alpha', lambda W, H, v: cta(W, H, 380 if v else 130, ['Build your', 'Vault.'], SUB)),
    ],
    '2026-11-black-friday': [
        ('01_hook', lambda W, H, v: hook(W, H, 420 if v else 140, ['Black Friday', 'pack hunt?'],
                                         ['Check Stock Radar first.'], 'BEAT THE SCALPERS')),
        ('02_map', lambda W, H, v: shot(W, H, 220 if v else 80, 'STOCK RADAR', ['See which stores', 'near you have packs'], MAP)),
        ('03_store', lambda W, H, v: shot(W, H, 220 if v else 90, 'CROWD-CONFIRMED', ['Crawlers report stock', 'in real time'], STORE, border=GREEN,
                                          note=['Spot packs on the shelf? One tap', 'and every crawler nearby knows.'])),
        ('04_join_alpha', lambda W, H, v: cta(W, H, 380 if v else 130, ['Hunt smarter.'], SUB)),
    ],
    '2026-11-community': [
        ('01_hook', lambda W, H, v: hook(W, H, 420 if v else 140, ['Help build', 'DCCards.'],
                                         ['Request features. Report bugs.', "Shape what's next."], 'JOIN THE CREW')),
        ('02_where', lambda W, H, v: textslide(W, H, 300 if v else 120, 'FIND US', ['Built with crawlers,', 'for crawlers'],
                                               ['DCCards is made by a fan, and the', 'roadmap comes from you.'],
                                               [('DISCORD', 'discord.gg/SUpuY28xhY'), ('REDDIT', 'r/DCCardsApp')])),
        ('03_join_alpha', lambda W, H, v: cta(W, H, 380 if v else 130, ['Get in early.'], SUB)),
    ],
    '2026-11-countdown': [
        ('01_hook', lambda W, H, v: hook(W, H, 420 if v else 140, ['2 days.'],
                                         ['DCCards hits the App Store', 'December 1.'], 'LAUNCH COUNTDOWN')),
        ('02_vault', lambda W, H, v: shot(W, H, 220 if v else 80, 'TRACK', ['All 188 cards.', 'Every pull.'], VAULT)),
        ('03_social', lambda W, H, v: shot(W, H, 220 if v else 80, 'SHOW OFF & TRADE', ['Your pulls,', 'your people'], FEED, border=PINK)),
        ('04_ready', lambda W, H, v: cta(W, H, 380 if v else 130, ['Be ready.'], SUB, kicker='DECEMBER 1', cta_text='dccardsapp.com')),
    ],
    '2026-12-launch': [
        ('01_hook', lambda W, H, v: hook(W, H, 420 if v else 140, ["It's here."],
                                         ['DCCards is live on', 'the App Store.'], 'DOWNLOAD NOW')),
        ('02_vault', lambda W, H, v: shot(W, H, 220 if v else 80, 'YOUR VAULT', ['All 188 cards.', 'Every pull, tracked.'], VAULT)),
        ('03_prices', lambda W, H, v: shot(W, H, 220 if v else 80, 'LIVE MARKET STATS', ['Real eBay', 'sold prices'], CHART, border=GREEN)),
        ('04_social', lambda W, H, v: shot(W, H, 220 if v else 80, 'CRAWLER SOCIAL', ['Post pulls.', 'Trade with crawlers.'], FEED, border=PINK)),
        ('05_radar', lambda W, H, v: shot(W, H, 220 if v else 80, 'STOCK RADAR', ['Find packs before', 'the scalpers do'], MAP)),
        ('06_download', lambda W, H, v: cta(W, H, 380 if v else 130, ['Welcome to the', 'dungeon, crawler.'], SUB,
                                            kicker='OUT NOW ON IPHONE', cta_text='Get it at dccardsapp.com')),
    ],
}


def build(key):
    out = f'{MEDIA}/posts/{key}/'; os.makedirs(out + 'instagram_carousel', exist_ok=True)
    slides = POSTS[key]
    for name, fn in slides:
        fn(1080, 1350, False).convert('RGB').save(f'{out}instagram_carousel/{name}.png')
    # video: same story on 1080x1920, slow zoom + crossfades, silent audio track
    W, H, FPS, XF = 1080, 1920, 30, 0.35
    secs = [3.2] + [4.2] * (len(slides) - 2) + [4.0]
    frames = [(fn(W, H, True).convert('RGB'), s) for (_, fn), s in zip(slides, secs)]
    vid = f'{out}DCCards_{key[8:].replace("-", "_")}_reel_1080x1920.mp4'
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-shortest', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20',
                           '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', vid], stdin=subprocess.PIPE)

    def fr(img, i, n, z1):
        z = 1 + (z1 - 1) * ease(i / max(1, n - 1)); w, h = int(W / z), int(H / z)
        return img.crop(((W - w) // 2, (H - h) // 2, (W - w) // 2 + w, (H - h) // 2 + h)).resize((W, H), Image.BILINEAR)
    black = Image.new('RGB', (W, H), BG); xn = int(XF * FPS)
    for si, (img, s) in enumerate(frames):
        n = int(s * FPS); z1 = 1.04 if si in (0, len(frames) - 1) else 1.06
        for i in range(n):
            f = fr(img, i, n, z1)
            if si == 0 and i < xn: f = Image.blend(black, f, i / xn)
            if si < len(frames) - 1 and i >= n - xn: f = Image.blend(f, frames[si + 1][0], (i - (n - xn)) / xn)
            ff.stdin.write(f.tobytes())
    ff.stdin.close(); ff.wait()
    frames[0][0].save(vid.replace('_1080x1920.mp4', '_cover.jpg'), quality=92)
    print('built', key)


if __name__ == '__main__':
    for k in (sys.argv[2:] or POSTS): build(k)
