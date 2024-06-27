# Clojure Web Shop
## Intro
The task at hand was to implement a parallelization of an e-commerce system for which a sequential implementation had been provided. We were to use the concurrency mechanisms taught in class in order to ensure correctness of data manipulation. In my implementation, the first step was to identify where conflicts would arise and I would end up with corrupt data.

When the stores being accessed are different and there is no sale, then there is no conflict. However, if the stores are the same, or there is a sale happening  concurrently with a process customer transaction, then there may be a conflict. The goal is to handle these conflicting cases in particular. In my implementation I used refs as I find that their synchronized and coordinated nature of managing state rather important in this exercise.
With regards to experimentation, I focused on the number of threads being used by the parallel implementation, the number of customers, and sale duration. I varied the number of threads between 2, 4 and 8, the number of customers from 50 to 2000, and the sales periods between 2 to 50 for time between sales and 5 to 20 for time of sales.

## Implementation
In the implementation, I used refs as mentioned earlier as I wanted to leverage the synchronization and coordination in order to ensure correctness of the implementation. Particularly, the prices
and the stock are what I changed to be refs. This is because during a sale, the prices are what change and this could be in conflict with an ongoing customer process. As such we want to ensure
that if the price changes, then the customer transaction would abort and restart. Similarly for stock, I made it a ref because multiple customers may access this at the same time and I wanted
to ensure that one would abort and retry later.

The entire process-customer block is wrapped in a dosync to ensure it fully aborts without committing its changes if it has to. The process-customers function on the other hand will always submit a new task to the thread pool. This task will be the process-customer task for each new customer. I use a fixed thread pool defined in the main function as shown below. This allows me to fix and vary the number of threads for bench-marking in order to find the optimal
number of threads.

```
(defn main [threads]
  (def pool (Executors/newFixedThreadPool threads))
    ...
```
In order to ensure correctness, I posed a couple of tests to my implementation. The first was to ensure that if there are not enough items in stock, the transaction does not alter the stock.
For instance, if our stock looks like this

```
(def stock
  ; Aldi
  [
    [14] ; Apple
    [2] ;Avocado
  ]
)
```

And our customers looked like this: 
```
(def customers
  [
    {:id 0 :products [["Apple" 7] ["Avocado" 3]]}
    {:id 1 :products [["Apple" 9] ["Avocado" 3]]}
  ]
)
```
It is clear to see that neither customer can be processed because they both need 3 avocados when there are only 2 in stock. In my implementation, the final stock is always the same as the initial
stock because none of the customers attained what they were looking for.

The second test I performed to ensure correctness was that if there are 2 customers and one product and store such that only one customer can be serviced, then only one customer should be serviced. This ensures that we never end up with negative stock. Consider if we have stock that looks like this: 
```
(def stock
  ; Aldi
  [
    [14] ; Apple
  ]
)
```
And our customers looked like this: 
```
(def customers
  [
    {:id 0 :products [["Apple" 7] ]}
    {:id 1 :products [["Apple" 9] ]}
  ]
)
```
hen in this situation, if it were sequential, only the first customer would ever get processed. However in parallel, we want to ensure that only one of them will get processed. Since stock is
a ref, if both customers are executed in parallel, then one of the transactions will have to abort. The final stock will either have 7 or 5 apples left in stock. This is exactly what I got in my
implementation.

Finally, because the sales alter the price and we already defined the price as a ref, then the set price method also uses a dosync block to ensure that changes to price are all coordinated and
no dirty reads occur.

```
(defn- set-price [store-id product-id new-price]
  "Set the price of the given product in the given store to ‘new-price‘."
  (dosync
    (alter prices assoc-in [product-id store-id] new-price)
  )
)
```