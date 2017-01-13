;;; Build rules from trajectories, e.g. test-trace.csv

;;; Use Common Lisp to compile and run. SBCL recommended.

;;; Input: trajectory file, every line is a trajectory (e.g. global shipping)
;;; test-trace.csv is supplied.
;;; first element is identifier for the element that is moving (e.g. vessel id),
;;; others are places (e.g. ports)
;;; min length of trajectory (defaut 8)
;;; max order (to prevent the search from growing infinitely) (default 5)
;;; distance method (default KL divergence)
;;; (distance tolerance: deprecated)
;;; min support
;;; digits for testing (not used for building rules) (default 3)

;;; output: rules of variable lengths, and frequencies (e.g. A,B,C -> D 45)
;;; output can be used for building Higher-Order Network (HON)


;;; Note: for support, there are two ways to compute
;;; The default way is to count every observation.
;;; Another way is to neglect redundant observations for same vessel (trajectory)
;;; In other words, support is # of trajectories containing the observation
;;; If the other way needs to be used, change push to pushnew in save-observations

;;; Note: for data other than trajectories, such as diffusion data,
;;; change ExtractSubSequences such that it only takes the newest entity sequence.

;;; Code can also be easily parallelized using pmapcar in lparallel
;;; if compiler supports multithreading.

;;; Jian Xu, 2015-02-19

;;; Note: changed from cosine distance to KL divergence
;;; (eliminating the need of tolerance parameter)

;;; Note: optimized performance on large data sets
;;; Jian Xu, 2016-02-18


;(declaim (optimize (debug 3)))

(defparameter *input-data-file* "traces-simulated-mesh-v100000-t100-mo4.csv")

(defparameter *min-length-of-trajectory* 8) 
(defparameter *max-length-of-trajectory* 100) 
(defparameter *max-order* 5)
(defparameter *distance-method* "kl")

(defparameter *distance-tolerance* 0.1)
(defparameter *min-support* 5)
(defparameter *digits-for-testing* 3) 

(defparameter *output-rules-file* "rules-synthetic.csv")
(defparameter *filter-bots* nil)



;;; data
;; vessel -> trajectory except last xxx steps
(defparameter *training* (make-hash-table :test #'equal))
(defparameter *testing* nil)
;; observations such as A B -> C support (v1 v2 v4)
(defparameter *observations* (make-hash-table :test #'equal))
(defparameter *rules* (make-hash-table :test #'equal))
(defparameter *distributions* (make-hash-table :test #'equal))
(defparameter *distributions-keys* nil)
(defparameter *children-lookup* (make-hash-table :test #'equal))



;;;;;;;;;;;;;;;
;;; updated 2014-11-20

(require :split-sequence)
(use-package :split-sequence)

;(ql:quickload 'lparallel)
;(require :lparallel)
(defun read-lines-from-file (filename)
  (printf "read file")
  (with-open-file (stream filename)
    (loop for line = (read-line stream nil)
          while line
          collect line)))

(defun split-line (deliminator line)
  (split-sequence:split-sequence deliminator line))

(defun read-lines-from-file-and-split (deliminator filename)
  (printf "read file")
  (with-open-file (stream filename)
    (loop for line = (read-line stream nil)
          while line
          collect (split-line deliminator line))))

(defun convert-pair-to-hash-table (pairs)
  (let ((dict (make-hash-table :test #'equal)))
    (dolist (pair pairs)
      (let ((key (first pair))
            (val (second pair)))
        (setf (gethash key dict) val)))
    dict))

(defmacro printf (stuff)
  `(progn (print ,stuff)
          (finish-output t)))

(defun parse-lists-for-integer (trajectories)
  (loop for trajectory in trajectories
        collect (mapcar #'parse-integer trajectory)))

(defun hash-keys (hash-table)
  (loop for key being the hash-keys of hash-table collect key))

(defun hash-values (hash-table)
  (loop for value being the hash-values of hash-table collect value))

;;;;;;;;;;;;;;;;;;

(defun filter-by-min-length (trajectories)
  (remove-if #'(lambda (trajectory) (< (length trajectory)
                                       (1+ *min-length-of-trajectory*)))
             trajectories))

(defun filter-by-max-length (trajectories)
  (remove-if #'(lambda (trajectory) (> (length trajectory)
                                       (1+ *max-length-of-trajectory*)))
             trajectories))

(defun filter-by-bots (trajectories)
  (if *filter-bots*
      (remove-if #'(lambda (trajectory) (member "43" trajectory :test #'string=))
                 trajectories)
      trajectories))

(defun build-training (trajectories)
  (printf "build training")
  (dolist (trajectory trajectories)
    (let* ((vessel (first trajectory))
           (ports (cdr trajectory))
           (training-ports (subseq ports 0 (- (length ports)
                                              *digits-for-testing*))))
      (setf (gethash vessel *training*) training-ports))))

(defun build-observations ()
  (printf "building observations")
  (loop for order from 1 to *max-order*
        do (build-observations-for-order order))
  (clrhash *training*) ; release space occupied by *training*
  )

(defun build-observations-for-order (order)
  (loop for vessel being the hash-keys in *training*
        do (build-observations-for-vessel order vessel)))

;;; change this function to take only the most recent steps as subsequences,
;;; instead of all possible subsequences.
(defun build-observations-for-vessel (order vessel)
  (let ((trajectory (gethash vessel *training*)))
    (dotimes (starting (- (length trajectory)
                          order))
      (let* ((observation (reverse (subseq trajectory starting (+ 1
                                                                  (+ starting order)))))
             (to (pop observation))
             (from (reverse observation)))
        ;(printf `(,from ,to ,vessel))
        (save-to-observations from to vessel)))))

(defun save-to-observations (from to vessel)
  (if (null (gethash from *observations*))
      (setf (gethash from *observations*) (make-hash-table)))
  (if (null (gethash to (gethash from *observations*)))
      (setf (gethash to (gethash from *observations*)) nil))
  ;;; Change the following line pushnew <-> push to change "support"
  ;(pushnew vessel (gethash to (gethash from *observations*))))
  (push vessel (gethash to (gethash from *observations*))))


(defun cleanup ()
  (defparameter *training* (make-hash-table :test #'equal))
  (defparameter *testing* nil)
  (defparameter *observations* (make-hash-table :test #'equal))
  (defparameter *rules* (make-hash-table :test #'equal))
  (defparameter *distributions* (make-hash-table :test #'equal))
  (defparameter *children-lookup* (make-hash-table :test #'equal))
  (defparameter *distributions-keys* nil)
  ;(gc :full t) ;; force garbage collection to save memory; SBCL only
)

;; The following puts restriction of min support for "from"
(defun build-distributions-support-for-from ()
  (printf "building distributions")
  (dolist (from (hash-keys *observations*))
    (let ((to-options (gethash from *observations*))
          (support -1))
      ;; compute support
      (setf support
            (apply #'+ (mapcar #'(lambda (x) (length x))
                               (hash-values to-options))))
      (when (>= support *min-support*)
        (setf (gethash from *distributions*) nil)
        (setf (getf (gethash from *distributions*) :support)
              support)
        ;; compute probabilitites
        (setf (getf (gethash from *distributions*) :distribution) (make-hash-table))
        (dolist (to (hash-keys to-options))
          (setf (gethash to (getf (gethash from *distributions*) :distribution))
                (/ (length (gethash to to-options))
                   support))))))
  (clrhash *observations*) ; free it to save space
)


;; The following puts restriction of min support for every path (for "to")
(defun build-distributions ()
  (printf "building distributions")
  (dolist (from (hash-keys *observations*))
    (let ((to-options (gethash from *observations*))
          (support -1))
      ;; compute support
      (setf support
            (apply #'+ (remove-if #'(lambda (x) (< x *min-support*))
                                  (mapcar #'(lambda (x) (length x))
                                          (hash-values to-options)))))
      (when (>= support *min-support*)
        (setf (gethash from *distributions*) nil)
        (setf (getf (gethash from *distributions*) :support)
              support)
        ;; compute probabilitites
        (setf (getf (gethash from *distributions*) :distribution) (make-hash-table))
        (dolist (to (remove-if #'(lambda (x) (< (length (gethash x to-options))
                                                *min-support*))
                               (hash-keys to-options)))
          (setf (gethash to (getf (gethash from *distributions*) :distribution))
                (/ (length (gethash to to-options))
                   support))))))
  (clrhash *observations*) ; free it to save space
  )

(defun generate-all-rules ()
  (printf "generating all rules")
  (let ((order-1-froms (remove-if #'(lambda (from) (> (length from)
                                                             1))
                                  *distributions-keys*))
        (counter 1))
    ;(printf (length order-1-froms))
    (dolist (from order-1-froms)
      (add-to-rules from) ;;;;;;;;;; Newly added! All first order rules should be added. Jian 2015-08-23
      (printf `(,counter "/" ,(length order-1-froms)))
      (incf counter)
      (extend-rule from from 1))))
    ;(lparallel.cognate:pmapcar (lambda (from) (extend-rule from from 1))
    ;                           order-1-froms)))

(defun extend-rule (valid-from curr-from order)
  ;; valid-from: last known "from"  with significantly different distrib.
  ;; if min-support or max-order is not met, valid-from will be added
  ;; to *rules* instead of growing children.
  ;; curr-from: current "from" or parent of the ongoing search.
  ;; If a new child with significantly different distribution is found,
  ;; this process will do recursion with the discovered child as new valid-from
  ;; otherwise keep growing with previous valid-from

  ;; if reaches max order, add valid-from to rules and stop
  (if (> (1+ order)
         *max-order*)
      (add-to-rules valid-from)
      (let* ((parent (gethash valid-from *distributions*))
             (parent-distribution (getf parent :distribution))
             (new-order (1+ order))
             (children-from (get-children curr-from)))
             ;(children-from (remove-if #'(lambda (from)
             ;                              ;; if length is not what we want
             ;                              (or (/= new-order
             ;                                      (length from))
             ;                                  ;; or if tail is not the same
             ;                                  (not (equal (cdr from)
             ;                                              curr-from))))
             ;                          *distributions-keys*)))
        ;(when (equal '(1716) valid-from)
          ;(printf `("v" ,valid-from "c" ,curr-from "o" ,order "c" ,children-from)))
        ;; if no further rules available, add valid-from to *rules*
        (if (null children-from)
            (add-to-rules valid-from)
            (dolist (child-from children-from)
              (let* ((child (gethash child-from *distributions*))
                     (child-support (getf child :support)))
                                        ; test support: if insufficient, add valid-from to rules and stop)
                                        ; always true for new distribution function
                (if (< child-support *min-support*)
                    (add-to-rules valid-from)
                    (let ((child-distribution (getf child :distribution)))
                                        ; test distribution: if similar, grow and keep valid-from
                                        ; if not similar, set new valid-from and grow recursively
                      ;(printf "enough support")
                      ;(printf "child")
                      ;(maphash #'(lambda (k v) (format t "~a => ~a~%" k v)) child-distribution)
                      ;(printf "parent")
                      ;(maphash #'(lambda (k v) (format t "~a => ~a~%" k v)) parent-distribution)
                      ;(printf (cosine-similarity child-distribution parent-distribution))
                      ;(printf (distribution-similar child-distribution parent-distribution))
                      ;(print (kl-divergence child-distribution parent-distribution))
                      ;(print (/ order child-support))
                      ;(print (distribution-similar child-distribution parent-distribution child-support order))
                      ;(finish-output t)
                      (if (distribution-similar child-distribution
                                                parent-distribution
                                                child-support
                                                new-order)
                          (extend-rule valid-from child-from new-order)
                          (extend-rule child-from child-from new-order))))))))))

;; use predefined distance method to compute distance between vector a and b
;; a and b are hash tables, probably having different keys
;; if key is present in a but not in b, set it 0
;; compare the distance with distance threshold to say if a and b are similar
(defun distribution-similar (a b child-support order)
  (if (equal *distance-method* "cosine")
      (if (<= (- 1
                 (cosine-similarity a b))
              *distance-tolerance*)
          t
          nil))

  (if (equal *distance-method* "kl")
      (if (<= (kl-divergence a b)
              (/ order (log (1+ child-support)
                            2)))
          t
          nil)))

(defun kl-divergence (a b)
  (let ((divergence 0))
    (dolist (to (hash-keys a))
      (incf divergence (* (get-probability to a)
                          (log (/ (get-probability to a)
                                  (get-probability to b))
                               2))))
    divergence))

(defun sum-of-squares (ht)
  (loop for item being the hash-values in ht
        summing (* item item)))

(defun get-probability (key ht)
  (if (null (gethash key ht))
      0
      (gethash key ht)))

(defun cosine-similarity (a b)
  (let ((union-toos (union (hash-keys a) (hash-keys b)))
        (sum-upper 0))
    (dolist (to union-toos)
      (incf sum-upper (* (get-probability to a)
                         (get-probability to b))))
    (/ sum-upper
       (* (sqrt (sum-of-squares a))
          (sqrt (sum-of-squares b))))))

;; Iteratively add rules and preceeding rules to rules list for easy building of network representation
(defun add-to-rules (from)
  (when (not (null from))
    (setf (gethash from *rules*) (gethash from *distributions*))
    (add-to-rules (butlast from))))
  ;(maplist #'(lambda (x) (setf (gethash x *rules*) (gethash x *distributions*)))
  ;         from))
  ;(setf (gethash from *rules*) (gethash from *distributions*)))

(defun output-rules ()
  (printf "writing all rules")
  (with-open-file (stream *output-rules-file*
                          :Direction :Output
                          :If-exists :supersede
                          :if-does-not-exist :create)
    (loop for from being the hash-keys in *rules*
          do (loop for to being the hash-keys in (getf (gethash from *rules*) :distribution)
                   do (format stream "~{~a ~}=> ~a ~f~%" from to (gethash to (getf (gethash from *rules*) :distribution)))))))

;; to speed up lookups when data is huge
;; added 2016/02/18
(defun build-children-lookup ()
  (printf "building children lookup")
  (dolist (key *distributions-keys*)
    (let ((prevs (cdr key)))
      (if (null (gethash prevs *children-lookup*))
          (setf (gethash prevs *children-lookup*) nil))
      (push key (gethash prevs *children-lookup*)))))

(defun get-children (from)
  (if (null (gethash from *children-lookup*))
      nil
      (gethash from *children-lookup*)))

(defun main ()
  (cleanup)
  (build-training (parse-lists-for-integer (filter-by-bots (filter-by-max-length (filter-by-min-length (read-lines-from-file-and-split #\Space *input-data-file*))))))
  (build-observations)
  (build-distributions)
  (setf *distributions-keys* (hash-keys *distributions*))
  (build-children-lookup)
  (generate-all-rules)
  (output-rules)
  (printf "finished")
  )
