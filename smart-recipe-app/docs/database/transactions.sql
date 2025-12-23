-- ==========================================
-- トランザクション処理の実装例
-- ==========================================

-- 例1: レシピを調理して在庫を消費
BEGIN TRANSACTION;

INSERT INTO cooking_history (user_id, recipe_id, rating, notes)
VALUES (1, 5, 5, '美味しかった！');

UPDATE user_inventory
SET is_consumed = TRUE,
    updated_at = CURRENT_TIMESTAMP
WHERE user_id = 1
  AND ingredient_id IN (
    SELECT ingredient_id 
    FROM recipe_ingredients 
    WHERE recipe_id = 5
  )
  AND is_consumed = FALSE;

COMMIT;