#!/bin/bash
#SBATCH -J job.ph # Job name
#SBATCH -N 1 # Total # of nodes
#SBATCH --ntasks-per-node 48
#SBATCH -t 00:15:00 # Run time (hh:mm:ss)
#SBATCH -A DMR23048
#SBATCH -p small
#SBATCH --reservation=MATCSSI_Norm_June18

# Launch MPI code...
export PATHQE=/work2/05193/sabyadk/shared/EPW_6.1s/q-e

ibrun -n 48 $PATHQE/bin/pw.x -nk 8 -in scf.in > scf.out
ibrun -n 48 $PATHQE/bin/ph.x -nk 8 -in ph.in > ph.out
