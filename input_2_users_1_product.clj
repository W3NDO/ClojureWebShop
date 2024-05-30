(ns input-2-users-1-product)
;; This is supposed to simulate a situation where only 1 customer's order can be processed because there is not enough stock
; Products
(def products
  ["Apple"])

; Stores
(def stores
  ["Aldi"])

(def prices
  ; Aldi Carr Colr Delh Lidl
  [[0.25] ; Apple
  ])

(def stock
  ; Aldi Carr Colr Delh Lidl
  [[14] ; Apple
   ])


(def customers
  [{:id 0 :products [["Apple" 7]]}
   {:id 1 :products [["Apple" 9]]}])

; Time in milliseconds between sales periods
(def TIME_BETWEEN_SALES 50)
; Time in milliseconds of sales period
(def TIME_OF_SALES 10)