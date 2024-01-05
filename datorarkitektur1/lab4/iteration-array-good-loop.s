# an example of iteration where the sum of every word
# in an array is computed

    .data
start: .word 1,0,1,0,1,0,1, 0
    .word 1,0,1,0,1,0,1, 0
    .word 1,0,1,0,1,0,1, 0
    .word 1,0,1,0,1,0,1, 0
    .word 1,0,1,0,1,0,1, 0
    .word 1,0,1,0,1,0,1, 0
    .word 1,0,1,0,1,0,1, 0
    .word 1,0,1,0,1,0,1, 0
    
    .word 1,0,1,0,1,0,1, 0
    .word 1,0,1,0,1,0,1, 0
    .word 1,0,1,0,1,0,1, 0
    .word 1,0,1,0,1,0,1, 0
    .word 1,0,1,0,1,0,1, 0
    .word 1,0,1,0,1,0,1, 0
    .word 1,0,1,0,1,0,1, 0
    .word 1,0,1,0,1,0,1, 0
    
    .word 1,0,1,0,1,0,1, 0
    .word 1,0,1,0,1,0,1, 0
    .word 1,0,1,0,1,0,1, 0
    .word 1,0,1,0,1,0,1, 0
    .word 1,0,1,0,1,0,1, 0
    .word 1,0,1,0,1,0,1, 0
    .word 1,0,1,0,1,0,1, 0
    .word 1,0,1,0,1,0,1, 0
    
    .word 1,0,1,0,1,0,1, 0
    .word 1,0,1,0,1,0,1, 0
    .word 1,0,1,0,1,0,1, 0
    .word 1,0,1,0,1,0,1, 0
    .word 1,0,1,0,1,0,1, 0
    .word 1,0,1,0,1,0,1, 0
    .word 1,0,1,0,1,0,1, 0
    .word 1,0,1,0,1,0,1, 0
    
#Total dataset size (from label "start" to end) is 1024 Bytes 

.text
.globl main

main: 
    add $t2, $zero, $zero    # initialize sum
    add $t4, $zero, $zero    # initialize loop invariant to 0
    addi $t5, $zero, 10      # repeat loop 10 times (iteration count)

init: 
    la $t0, start            # load start address of array
    addi $t1, $t0, 1024      # address of end of array
    
loop: 
    lw $t3, 0($t0)           # fetch array element
    add $t2, $t2, $t3        # update sum
    addi $t0, $t0, 4         # point to next address

    bne $t1, $t0, loop       # if not done, start next iteration

out_loop:
    addi $t4, $t4, 1         # increment loop invariant by at the end of every iteration
    bne $t4, $t5, init       # if outer-loop iteration count not reached start another iteration
    

finish:
    li $v0, 10
    syscall
