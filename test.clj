(ns test)

(import '(java.util.concurrent Executors))
(def pool (Executors/newFixedThreadPool 8))

(def today (ref "Monday"))
((dosync (ref-set today "Tuesday")))

(defn print-today [] ( println @today))

(print-today)