#INSTALL LIBRARY
#!pip install openpyxl -q

import cv2
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time
from google.colab import files

#PENGATURAN KEY
KEY_ITERATIONS = 15
KEY_R = 3.99
KEY_X0 = 0.1

#FUNGSI METRIK
def calculate_entropy(img):
    hist = cv2.calcHist([img], [0], None, [256], [0, 256])
    hist = hist.ravel() / hist.sum()
    hist = hist[hist > 0]
    return -np.sum(hist * np.log2(hist))

def calculate_correlation(img):
    h_list, v_list, d_list = [], [], []
    rows, cols = img.shape
    for i in range(rows - 1):
        for j in range(cols - 1):
            h_list.append((img[i, j], img[i, j + 1]))
            v_list.append((img[i, j], img[i + 1, j]))
            d_list.append((img[i, j], img[i + 1, j + 1]))

    h_arr = np.array(h_list)
    v_arr = np.array(v_list)
    d_arr = np.array(d_list)

    corr_h = np.corrcoef(h_arr[:, 0], h_arr[:, 1])[0, 1]
    corr_v = np.corrcoef(v_arr[:, 0], v_arr[:, 1])[0, 1]
    corr_d = np.corrcoef(d_arr[:, 0], d_arr[:, 1])[0, 1]
    return corr_h, corr_v, corr_d

def npcr_uaci(img1, img2):
    diff = np.abs(img1.astype(np.float32) - img2.astype(np.float32))
    npcr = (np.sum(diff != 0) / img1.size) * 100
    uaci = (np.sum(diff) / (img1.size * 255)) * 100
    return npcr, uaci

def calculate_metrics(original, encrypted):
    metrics = {}
    metrics["Entropy_Original"] = calculate_entropy(original)
    metrics["Entropy_Encrypted"] = calculate_entropy(encrypted)

    h_o, v_o, d_o = calculate_correlation(original)
    h_e, v_e, d_e = calculate_correlation(encrypted)

    metrics["Corr_H_Original"] = h_o
    metrics["Corr_V_Original"] = v_o
    metrics["Corr_D_Original"] = d_o
    metrics["Corr_H_Encrypted"] = h_e
    metrics["Corr_V_Encrypted"] = v_e
    metrics["Corr_D_Encrypted"] = d_e

    npcr, uaci = npcr_uaci(original, encrypted)
    metrics["NPCR"] = npcr
    metrics["UACI"] = uaci
    return metrics

#ARNOLD'S CAT MAP
def arnold_cat_map(img, iterations=10):
    h, w = img.shape
    result = np.zeros_like(img)
    for _ in range(iterations):
        for i in range(h):
            for j in range(w):
                new_i = (i + j) % h
                new_j = (i + 2 * j) % w
                result[new_i, new_j] = img[i, j]
        img = result.copy()
    return result

def inverse_arnold_cat_map(img, iterations=10):
    h, w = img.shape
    result = np.zeros_like(img)
    for _ in range(iterations):
        for i in range(h):
            for j in range(w):
                new_i = (2 * i - j) % h
                new_j = (-i + j) % w
                result[new_i, new_j] = img[i, j]
        img = result.copy()
    return result

#LOGISTIC MAP
def logistic_map_key(size, r=KEY_R, x0=KEY_X0):
    key = []
    x = x0
    for _ in range(size):
        x = r * x * (1 - x)
        key.append(int(x * 255) % 256)
    return np.array(key, dtype=np.uint8)

#ENKRIPSI & DEKRIPSI
def encrypt(img, iterations=KEY_ITERATIONS, r=KEY_R, x0=KEY_X0):
    start = time.time()
    confused = arnold_cat_map(img.copy(), iterations)
    flat = confused.flatten()
    key = logistic_map_key(len(flat), r, x0)
    encrypted = np.bitwise_xor(flat, key).reshape(img.shape)
    print(f"Waktu enkripsi: {time.time() - start:.4f} detik")
    return encrypted

def decrypt(encrypted, iterations=KEY_ITERATIONS, r=KEY_R, x0=KEY_X0):
    flat = encrypted.flatten()
    key = logistic_map_key(len(flat), r, x0)
    decrypted = np.bitwise_xor(flat, key).reshape(encrypted.shape)
    decrypted = inverse_arnold_cat_map(decrypted, iterations)
    return decrypted

#MAIN PROGRAM
print("Silakan upload gambar (bisa lebih dari 1 file)...")
uploaded = files.upload()

print(f"\nKey yang digunakan:")
print(f"  - Iterations : {KEY_ITERATIONS}")
print(f"  - r          : {KEY_R}")
print(f"  - x0         : {KEY_X0}")

all_results = []

for filename in uploaded.keys():
    print(f"\n{'='*55}")
    print(f"Sedang memproses: {filename}")
    print(f"{'='*55}")

    # Baca gambar
    file_bytes = np.frombuffer(uploaded[filename], np.uint8)
    original = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)

    if original is None:
        print(f"❌ Gagal membaca: {filename}")
        continue

    # Resize
    original = cv2.resize(original, (256, 256))

    # Enkripsi & Dekripsi
    encrypted = encrypt(original, iterations=KEY_ITERATIONS, r=KEY_R, x0=KEY_X0)
    decrypted = decrypt(encrypted, iterations=KEY_ITERATIONS, r=KEY_R, x0=KEY_X0)

    # Nama file bersih
    name_only = filename.rsplit('.', 1)[0]
    encrypted_filename = f"encrypted_{name_only}.png"
    decrypted_filename = f"decrypted_{name_only}.png"
    histogram_filename = f"histogram_{name_only}.png"

    # Simpan gambar
    cv2.imwrite(encrypted_filename, encrypted)
    cv2.imwrite(decrypted_filename, decrypted)

    # Hitung metrik
    metrics = calculate_metrics(original, encrypted)
    metrics["Nama_Citra"] = filename
    all_results.append(metrics)

    print(pd.DataFrame([metrics]).round(4).T)

    #GAMBAR + HISTOGRAM
    plt.figure(figsize=(15, 8))

    plt.subplot(2, 3, 1)
    plt.imshow(original, cmap='gray')
    plt.title("Original Image")
    plt.axis('off')

    plt.subplot(2, 3, 2)
    plt.imshow(encrypted, cmap='gray')
    plt.title("Encrypted Image")
    plt.axis('off')

    plt.subplot(2, 3, 3)
    plt.imshow(decrypted, cmap='gray')
    plt.title("Decrypted Image")
    plt.axis('off')

    plt.subplot(2, 3, 4)
    plt.hist(original.ravel(), bins=256, range=[0, 256], color='blue', alpha=0.7)
    plt.title("Histogram Original")

    plt.subplot(2, 3, 5)
    plt.hist(encrypted.ravel(), bins=256, range=[0, 256], color='red', alpha=0.7)
    plt.title("Histogram Encrypted")

    plt.subplot(2, 3, 6)
    plt.hist(decrypted.ravel(), bins=256, range=[0, 256], color='green', alpha=0.7)
    plt.title("Histogram Decrypted")

    plt.tight_layout()

    # Simpan histogram SEBELUM show
    plt.savefig(histogram_filename, dpi=150, bbox_inches='tight')
    plt.show()

    print(f"✅ File berhasil disimpan:")
    print(f"   - {encrypted_filename}")
    print(f"   - {decrypted_filename}")
    print(f"   - {histogram_filename}")

# Simpan Excel
if all_results:
    df = pd.DataFrame(all_results)
    cols = ["Nama_Citra"] + [c for c in df.columns if c != "Nama_Citra"]
    df = df[cols]
    df.to_excel("hasil_semua_metrik.xlsx", index=False)

    print("\n✅ Hasil metrik berhasil disimpan ke 'hasil_semua_metrik.xlsx'")
    print("👉 Untuk download semua file, jalankan cell baru:")
else:
    print("\n❌ Tidak ada gambar yang berhasil diproses.")


# Sabotase untuk menguji Jenkins
password_database = "admin12345" 
print(password_database)