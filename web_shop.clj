(ns web-shop
  (:require [clojure.pprint] ; For 'pretty-printing'
            ; Choose one of the input files below.
            ;[input-simple :as input]
            [input-random :as input]
            ;[input-no-customer-processed :as input]
            ;[input-2-users-1-product :as input]
            ))


; Logging
(def logger (agent nil))
;(defn log [& msgs] (send logger (fn [_] (apply println msgs)))) ; uncomment this to turn ON logging
(defn log [& msgs] nil) ; uncomment this to turn OFF logging


; We simply copy the products from the input file, without modifying them.
(def products input/products)

(defn product-name->id [name]
  "Return id (= index) of product with given `name`.
  E.g. (product-name->id \"Apple\") = 0"
  (.indexOf products name))

(defn product-id->name [id]
  "Return name of product with given `id`.
  E.g. (product-id->name 0) = \"Apple\""
  (nth products id))


; We simply copy the stores from the input file, without modifying them.
(def stores input/stores)

(defn store-name->id [name]
  "Return id (= index) of store with given `name`.
  E.g. (store-name->id \"Aldi\") = 0"
  (.indexOf stores name))

(defn store-id->name [id]
  "Return name of store with given `id`.
  E.g. (store-id->name 0) = \"Aldi\""
  (nth stores id))


; We wrap the prices from the input file in a single atom in this
; implementation. You are free to change this to a more appropriate mechanism.
(def prices (atom input/prices))

(defn- get-price [store-id product-id]
  "Returns the price of the given product in the given store."
  (nth (nth @prices product-id) store-id))

(defn- get-total-price [store-id product-ids-and-number]
  "Returns the total price for a given number of products in the given store."
  (reduce +
    (map
      (fn [[product-id n]]
        (* n (get-price store-id product-id)))
      product-ids-and-number)))

(defn- set-price [store-id product-id new-price]
  "Set the price of the given product in the given store to `new-price`."
  (swap! prices assoc-in [product-id store-id] new-price))


; We wrap the stock from the input file in a single atom in this
; implementation. You are free to change this to a more appropriate mechanism.
(def stock (atom input/stock))

(defn print-stock [stock]
  "Print stock. Note: `stock` should not be an atom/ref/... but the value it
  contains."
  (println "Stock:")
  ; Print header row with store names (abbreviated to four characters)
  (doseq [store stores]
    (print (apply str (take 4 store)) ""))
  (println)
  ; Print table
  (doseq [product-id (range (count stock))]
    ; Line of numbers
    (doseq [number-in-stock (nth stock product-id)]
      (print (clojure.pprint/cl-format nil "~4d " number-in-stock)))
    ; Name of product
    (println (product-id->name product-id))))

(defn- product-available? [store-id product-id n]
  "Returns true if at least `n` of the given product are still available in the
  given store."
  (>= (nth (nth @stock product-id) store-id) n))

(defn- buy-product [store-id product-id n]
  "Updates `stock` to buy `n` of the given product in the given store."
  (swap! stock
    (fn [old-stock]
      (update-in old-stock [product-id store-id]
        (fn [available] (- available n))))))

(defn- find-available-stores [product-ids-and-number]
  "Returns the id's of the stores in which the given products are still
  available."
  (filter
    (fn [store-id]
      (every?
        (fn [[product-id n]] (product-available? store-id product-id n))
        product-ids-and-number))
    (map store-name->id stores)))


(defn buy-products [store-id product-ids-and-number]
  (doseq [[product-id n] product-ids-and-number]
    (buy-product store-id product-id n)))

(defn- process-customer [customer]
  "Process `customer`. Consists of three steps:
  1. Finding all stores in which the requested products are still available.
  2. Sorting the found stores to find the cheapest (for the sum of all products).
  3. Buying the products by updating the `stock`.

  Note: because this implementation is sequential, we do not suffer from
  inconsistencies. That will be different in your implementation."
  (let [product-ids-and-number
          (map (fn [[name number]] [(product-name->id name) number])
            (:products customer))
        available-store-ids  ; step 1
          (find-available-stores product-ids-and-number)
        cheapest-store-id  ; step 2
          (first  ; Returns nil if there's no available stores
            (sort-by
              ; sort stores by total price
              (fn [store-id] (get-total-price store-id product-ids-and-number))
              available-store-ids))]
    (if (nil? cheapest-store-id)
      (log "Customer" (:id customer) "could not find a store that has"
        (:products customer))
      (do
        (buy-products cheapest-store-id product-ids-and-number) ;  step 3
        (log "Customer" (:id customer) "bought" (:products customer) "in"
          (store-id->name cheapest-store-id))))))

(def finished-processing?
  "Set to true once all customers have been processed, so that sales process
  can end."
  (atom false))

(defn process-customers [customers]
  "Process `customers` one by one. In this code, this happens sequentially. In
  your implementation, this should be parallelized."
  (doseq [customer customers]
    (process-customer customer))
  (reset! finished-processing? true))


(defn start-sale [store-id]
  "Sale: -10% on `store-id`."
  (log "Start sale for store" (store-id->name store-id))
  (doseq [product-id (range (count products))]
    (set-price store-id product-id (* (get-price store-id product-id) 0.90))))

(defn end-sale [store-id]
  "End sale: reverse discount on `store-id`."
  (log "End sale for store" (store-id->name store-id))
  (doseq [product-id (range (count products))]
    (set-price store-id product-id (/ (get-price store-id product-id) 0.90))))

(defn sales-process []
  "The sales process starts and ends sales periods, until `finished-processing?`
  is true."
  (loop []
    (let [store-id (store-name->id (rand-nth stores))]
      (Thread/sleep input/TIME_BETWEEN_SALES)
      (start-sale store-id)
      (Thread/sleep input/TIME_OF_SALES)
      (end-sale store-id))
    (if (not @finished-processing?)
      (recur))))


(defn main []
  ; Print parameters
  (println "Number of products:" (count products))
  (println "Number of stores:" (count stores))
  (println "Number of customers:" (count input/customers))
  (println "Time between sales:" input/TIME_BETWEEN_SALES)
  (println "Time of sales:" input/TIME_OF_SALES)
  ; Print initial stock
  (println "Initial stock:")
  (print-stock @stock)
  ; Start two threads: one for processing customers, one for sales.
  ; Print the time to execute the first thread.
  (let [f1 (future (time (process-customers input/customers)))
        f2 (future (sales-process))]
    ; Wait until both have finished
    @f1
    @f2
    (await logger))
  ; Print final stock, for manual verification and debugging
  (println "Final stock:")
  (print-stock @stock))

(main)
(shutdown-agents)
