(ns input-no-customer-processed)
;; This is supposed to simulate a situation where no orders are processed because neither customer can clear their cart

; Products
(def products
  ["Apple" "Avocado"])

; Stores
(def stores
  ["Aldi"])

; The price of each item in each store.
;
; An apple costs €0.25 in Aldi, €0.30 in Carrefour, etc.
(def prices
  ; Aldi Carr Colr Delh Lidl
  [[0.25] ; Apple
   [0.77]])

; The number of items left of each item in each store.
;
; E.g. there are 15 apples left at Aldi, 25 apples at Carrefour, etc.
(def stock
  ; Aldi Carr Colr Delh Lidl
  [[14] ; Apple
   [2] ;Avocado
   ])

; Customers and the products they want to buy.
;
; E.g. customer 0 wants to buy 5 bananas and 7 apples.
(def customers
  [{:id 0 :products [["Apple" 7] ["Avocado" 3]]}
   {:id 1 :products [["Apple" 9] ["Avocado" 3]]}])

; Time in milliseconds between sales periods
(def TIME_BETWEEN_SALES 50)
; Time in milliseconds of sales period
(def TIME_OF_SALES 10)

(def thread_count [2 4 6 8])
