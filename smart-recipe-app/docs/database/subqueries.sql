-- ==========================================
-- 副文（サブクエリ）の実装例
-- ==========================================

-- 例1: 期限が近い食材を使うレシピを検索
SELECT 
    r.recipe_id,
    r.recipe_name,
    r.cooking_time
FROM recipes r
WHERE r.recipe_id IN (
    SELECT DISTINCT ri.recipe_id
    FROM recipe_ingredients ri
    INNER JOIN user_inventory ui 
        ON ri.ingredient_id = ui.ingredient_id
    WHERE ui.user_id = 1
      AND ui.is_consumed = FALSE
      AND ui.expiry_date <= CURRENT_DATE + INTERVAL '3 days'
)
ORDER BY r.recipe_name;