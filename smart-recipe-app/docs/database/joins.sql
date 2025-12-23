-- ==========================================
-- Join操作の実装例
-- ==========================================

-- 例1: ユーザーの在庫一覧（INNER JOIN）
SELECT 
    ui.inventory_id,
    ui.quantity,
    ui.expiry_date,
    im.ingredient_name,
    im.category
FROM user_inventory ui
INNER JOIN ingredients_master im 
    ON ui.ingredient_id = im.ingredient_id
WHERE ui.user_id = 1
  AND ui.is_consumed = FALSE
ORDER BY ui.expiry_date ASC;