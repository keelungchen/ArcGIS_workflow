import os
import arcpy
from samgeo import SamGeo2, regularize

# ---- 1) 輸入與輸出路徑設定 ----
ortho = "CJ_P1_2307_TWD_1mm_Clip.tif"                 # 你的正射影像
points_fc = "CL_P1_coral_points"       # 你的點圖層（可含 label 欄位）
label_field = "label"                            # 若無此欄位，程式會預設所有點為 1（正點）

out_workspace = r"D:\ArcGIS\AI_training\AI_training.gdb"                # 結果輸出 GDB
mask_tif = r"D:\ArcGIS\AI_training\sam2_mask.tif"              # 暫存：分割遮罩（GeoTIFF）

# 取得座標數量
count = int(arcpy.management.GetCount(points_fc)[0])
print(f"共有 {count} 個點")

# 轉成 [ [x, y], ... ] 格式
point_coords_batch = []
with arcpy.da.SearchCursor(points_fc, ["SHAPE@X", "SHAPE@Y"], where_clause="Shape IS NOT NULL") as cur:
    for x, y in cur:
        point_coords_batch.append([x, y])

# 印出結果（前幾筆檢查）
print("point_coords_batch =", point_coords_batch)

# 取得 SpatialReference 物件
# 取得 SpatialReference 物件
sr = arcpy.Describe(points_fc).spatialReference
# EPSG 代碼
epsg = sr.factoryCode
if epsg and int(epsg) > 0:
    point_crs = f"EPSG:{int(epsg)}"
else:
    # 如果沒有 EPSG，則輸出 WKT 字串
    point_crs = sr.exportToString()
print("座標系名稱:", sr.name)
print("EPSG 代碼:", epsg)
print("SAM2 要用的 point_crs:", point_crs)

# model_id 可選：'sam2-hiera-tiny' / 'sam2-hiera-small' / 'sam2-hiera-base' / 'sam2-hiera-large'
# 大模型更準但更耗記憶體。若 GPU 不強，先試 small/base。
sam = SamGeo2(model_id="sam2-hiera-small", automatic=False)

# 指定影像
sam.set_image("CJ_P1_2307_TWD_1mm_Clip.tif" )

# 進行點提示分割，輸出二值遮罩（uint8；1=物件，0=背景）
sam.predict_by_points(
    point_coords_batch=point_coords_batch,     # ✅ 直接丟 coords，不要 [coords]
    point_crs= "EPSG:3826",
    output="mask.tif",
    dtype="uint8",
)

sam.show_masks(cmap="binary_r")


