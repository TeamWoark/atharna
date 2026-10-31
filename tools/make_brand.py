from PIL import Image
import numpy as np, pathlib

src = Image.open('uploads/image-1.png').convert('RGB')
a = np.asarray(src).astype(np.float32)
bg = np.array([0x23,0x1F,0x20], dtype=np.float32)

diff = np.clip(a - bg, 0, None)
alpha = (diff.max(axis=2) / (255.0 - bg.min()))   # 0..1
alpha = np.clip(alpha, 0, 1)
# معالجة البكسلات شديدة القتامة
alpha[alpha < 0.06] = 0
with np.errstate(divide='ignore', invalid='ignore'):
    fg = bg + diff / np.maximum(alpha[...,None], 1e-6)
fg = np.clip(fg, 0, 255)

rgba = np.dstack([fg, alpha*255]).astype(np.uint8)
logo = Image.fromarray(rgba, 'RGBA')
bbox = logo.getbbox()
logo = logo.crop(bbox)
print('full', logo.size)
logo.save('assets/brand/logo-white.png')

# نسخة داكنة: تحويل الأبيض إلى الفحمي مع الحفاظ على البرتقالي
arr = np.asarray(logo).astype(np.float32)
r,g,b_,al = arr[...,0],arr[...,1],arr[...,2],arr[...,3]
neutral = (np.abs(r-g)<26) & (np.abs(g-b_)<26) & (r>120)
out = arr.copy()
for i,c in enumerate((0x23,0x1F,0x20)):
    ch = out[...,i]; ch[neutral] = c
Image.fromarray(out.astype(np.uint8),'RGBA').save('assets/brand/logo-dark.png')

# العلامة (بلس) والوردمارك
W,H = logo.size
mark = logo.crop((0, int(H*0.28), int(W*0.30), int(H*0.86))).crop(logo.crop((0,0,int(W*0.30),H)).getbbox())
mark.save('assets/brand/mark.png'); print('mark', mark.size)
word = logo.crop((int(W*0.24), 0, W, int(H*0.66)))
word = word.crop(word.getbbox())
word.save('assets/brand/wordmark.png'); print('word', word.size)

# نسخة مربعة للاستخدام كأيقونة
side = max(mark.size)
sq = Image.new('RGBA',(side,side),(0,0,0,0)); sq.paste(mark,((side-mark.size[0])//2,(side-mark.size[1])//2)); sq.save('assets/brand/mark-square.png')
print('done')
