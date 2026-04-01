---
layout: post
title: linalg math revision
date: 2026-03-28 05:40:00 +0800
draft: true
---

<style>
  
  .quiz-options {
    list-style: none;
    padding: 0;
    margin-top: 15px;
  }

  .option {
    padding: 10px 15px;
    margin-bottom: 8px;
    cursor: pointer;
    border: 1px solid gray;
    transition: all 0.2s ease;
  }

  .option:hover {
    border: 1px solid white;
  }

  .quiz-block.answered .option {
    cursor: default;
    pointer-events: none;
  }

  .quiz-block.answered .option.correct {
    background-color: #1c1c1c;
    color: green;
    font-weight: bold;
  }

  .quiz-block.answered .option:not(.correct) {
    color: #86181d;
    opacity: 0.7;
  }

  .explanation {
    display: none;
    margin-top: 25px;
    padding-inline: 15px;
    border-left: 2px solid #b8bb26;
  }

  .quiz-block.answered .explanation {
    display: block;
    animation: fadeIn 0.5s;
  }

  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }
</style>

recommended listening [weatherday's darling of loving vows](https://www.youtube.com/watch?v=kBbls4rJXUE)

![img](https://i.imgur.com/f0V3jSe.png)

honestly i struggled a lot with linalg theory, this is more for my own sake. not all of this might be tested, some of this might be out-of-scope but it's always good to gain an intuition

<div class="quiz-block" markdown="1">
### question 1

consider the matrix $ M = \begin{bmatrix} x_1 & y_1 \\\ x_2 & y_2 \end{bmatrix} $ such that $ M^{-1} = M^T $. further, define $ m_1 = \begin{bmatrix} x_1 \\\ y_1 \end{bmatrix} $ and $ m_2 = \begin{bmatrix} x_2 \\\ y_2 \end{bmatrix} $. which of the following is true? 

<ul class="quiz-options">
  <li class="option">$ M $ is a scaling transformation.</li>
  <li class="option correct">the magnitude of $ m_1 $ and $ m_2 $ are the same.</li>
  <li class="option">the determinant of $ M $ can never be 1.</li>
  <li class="option">the cross product of $ m_1 $ and $ m_2 $ is the zero vector.</li>
</ul>


<div class="explanation" markdown=1>
<b>explanation</b>: recall that $ M $ must be orthonormal (definitionally, as its transpose is its inverse). the definition of an orthonormal matrix is that its two vectors are orthogonal unit vectors, we can prove this by doing the math:

$$
\begin{align*}
M M^T &= I \\
\begin{bmatrix} x_1 & y_1 \\\ x_2 & y_2 \end{bmatrix}
\begin{bmatrix} x_1 & x_2 \\\ y_1 & y_2 \end{bmatrix} &= 
\begin{bmatrix} 1 & 0 \\\ 0 & 1 \end{bmatrix} \\
\begin{bmatrix} 1 & 0 \\\ 0 & 1 \end{bmatrix} &=
\begin{bmatrix} {x_1}^{2} & x_1 \cdot x_2 \\\ x_2 \cdot x_1 & {x_2}^{2} \end{bmatrix}
\end{align*}
$$

we can see that the dot product of $ x_1 $ and $ x_2 $ is 0, and that the dot product of both vectors with themselves is 1. if the dot product of two vectors is 0, they are orthogonal, and the dot product of a vector with itself is the square of its magnitude - if that's just 1, then the magnitude of those vectors must be 1,  hence they are unit vectors.

the rest are untrue for different reasons: 

orthonormal matrices are _rotational_ transforms (think about how mapping unit vectors onto another pair of orthogonal unit vectors would work, no scaling or shearing would be involved, just rotating).

you can also solve for the determinants:

$$
\begin{align*}
\det(MM^{-1}) &= \det(I) \\
\det(M) * \det(M^{-1}) &= 1
\end{align*}
$$

and since $ \det(M) = \det(M^{T}) $ you can see that the only possible solutions are either $ \det(M) = 1 $ or $ \det(M) = -1 $.

finally, given that we know that $ m_1 $ and $ m_2 $ are orthogonal, their dot products would be 0, not their cross products. whew.
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
  var options = document.querySelectorAll('.option');
  options.forEach(function(option) {
    option.addEventListener('click', function() {
      var block = event.currentTarget.closest('.quiz-block');
      console.log(block);
      if (block.classList.contains('answered')) return;
      block.classList.add('answered');
    });
  });
});
</script>


