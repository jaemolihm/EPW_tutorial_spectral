#!/bin/bash
#SBATCH -J myjob
#SBATCH -o myjob.o%j
#SBATCH -e myjob.e%j
#SBATCH -N 1
#SBATCH --ntasks-per-node 8
#SBATCH -t 00:15:00
#SBATCH -A DMR23048
#SBATCH -p small

# Launch MPI code...
export PATHQE=/work2/11514/acarrasc/frontera/q-e

ibrun -n 8 $PATHQE/bin/pw.x -nk 4 -in scf.in > scf.out
ibrun -n 8 $PATHQE/bin/ph.x -nk 4 -in ph.in > ph.out