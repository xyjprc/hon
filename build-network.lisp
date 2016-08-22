;;; builds High Order Network using rules generated with build-rules.

;;; Use Common Lisp to compile and run. SBCL recommended.

;;; Input: rules file (rules-test.csv) and highest order
;;; Output: network file in triples.
;;; C|A.B,E,0.3 means a vessel at port C (nth), coming from A (n-1th) and
;;; B (n-2th), the probability of going to E (n+1th) is 0.3

;;; Note: "from" is usually a list, with lengths from 1 to 5
;;; "to" can be EITHER a "string" (originally created) or a list (rewiring)

;;; Jian Xu, 2015-02-19

;;; parameters
(defparameter *input-rules-file* "rules-synthetic.csv")
(defparameter *max-order* 5)
(defparameter *output-network-file* "network-synthetic.csv")

;;; data
(defparameter *rules* nil)
(defparameter *network* (make-hash-table :test #'equal))
(defparameter *froms* nil)


;;; freq
;;; updated 2014-11-20

(declaim (optimize (debug 3)))


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

(defun cleanup ()
  (defparameter *rules* nil)
  (defparameter *network* (make-hash-table :test #'equal)))

(defun build-rules (lines)
  (dolist (line lines)
    (let* ((reversed-line (reverse line))
           (probability (pop reversed-line))
           (to (list (pop reversed-line)))
           (from (reverse (cdr reversed-line))))
      (push (list :from from :to to :probability probability) *rules*))))

;; note this adds ALL rules to network
(defun add-rules-to-network ()
  (printf "adding rules to network")
  (dolist (rule *rules*)
    (if (= 1
           (length (getf rule :from)))
        (add-rule-to-network rule)
        (add-high-order-rule-to-network rule))))

(defun add-high-order-rule-to-network (rule)
  (add-rule-to-network rule)
  (rewire rule))

(defun rewire (rule)
  (let* ((prev-from (butlast (getf rule :from)))
         (prev-to (last (getf rule :from)))
         (probability (gethash (list :from prev-from
                                     :to prev-to) *network*)))
    ;(printf `(,rule ,prev-from ,prev-to ,probability))

    ;; if rewiring necessary
    (when (null (gethash (list :from prev-from
                               :to (getf rule :from))
                         *network*))
      ;; add new wire, pointing A->B|A
      (setf (gethash (list :from prev-from
                           :to (getf rule :from))
                     *network*)
            probability)
      ;; remove old wire A->B
      (remhash (list :from prev-from
                     :to prev-to)
               *network*))))

;; note this adds SINGLE rule to network
(defun add-rule-to-network (rule)
  (setf (gethash (list :from (getf rule :from)
                       :to (getf rule :to))
                 *network*)
        (getf rule :probability)))

(defun output-network ()
  (printf "writing network")
  (with-open-file (stream *output-network-file*
                          :direction :output
                          :if-exists :supersede
                          :if-does-not-exist :create)
    (dolist (edge (hash-keys *network*))
      (format stream "~a|~{~a~^.~},~a|~{~a~^.~},~a~%"
              (car (last (getf edge :from)))
              (reverse (butlast (getf edge :from)))
              (car (last (getf edge :to)))
              (reverse (butlast (getf edge :to)))
              (gethash edge *network*)))))

(defun rewire-last-step (froms)
  (printf "rewiring last step")
  (let ((to-add nil)
        (to-remove nil))
    (dolist (edge (hash-keys *network*))
      (let ((from (getf edge :from))
            (to (getf edge :to))
            (probability (gethash edge *network*)))
        (if (= (length to) 1)
            (let ((new-to (append from to)))
              (loop while (> (length new-to)
                             1)
                    do (if (gethash new-to froms)
                           (progn (push (list (list :from from :to new-to)
                                              probability)
                                        to-add)
                                  (push (list :from from :to to) to-remove)
                                  (return))
                           (pop new-to)))))))
    (dolist (edge to-add)
      (setf (gethash (first edge) *network*) (second edge)))
    (dolist (edge to-remove)
      (remhash edge *network*))))

(defun generate-froms ()
  (let ((froms (make-hash-table :test #'equal)))
    (dolist (edge (hash-keys *network*))
      (setf (gethash (getf edge :from) froms) 1))
    froms))

(defun infer-dangling (froms)
  (let ((danglings nil))
    (dolist (edge (hash-keys *network*))
      (let ((to (getf edge :to)))
        (if (null (gethash to froms))
            (pushnew to danglings))))
    (dolist (dangling danglings)
      (printf dangling))))

(defun main()
  (cleanup)
  (build-rules (read-lines-from-file-and-split #\Space *input-rules-file*))
  (setf *rules* (sort *rules*
         #'<
         :key #'(lambda (x) (length (getf x :from)))))
  (add-rules-to-network)
  (setf *froms* (generate-froms))
  (rewire-last-step *froms*)
  ;(infer-dangling *froms*)
  (output-network)
  (printf "finished"))
