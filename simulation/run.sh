
echoinred() {
	echo -e '\e[0;31m'"$@"
	tput sgr0
}
# afficher en bleu le premier parametre
echoinblue() {
	echo -e '\e[0;34m'"$@"
	tput sgr0
}


# input_files="../experiments/CEA-curie/predicted_swf/*.swf ../experiments/CEA-curie/original_swf/*.swf"
input_files="./pyss/src/sample_input"

# simulated_files_dir=../experiments/CEA-curie/simulated_swf
simulated_files_dir=simulated_swf

# final_csv_file=../experiments/CEA-curie/results.csv
final_csv_file=results.csv

algos="FcfsScheduler ConservativeScheduler EasyBackfillScheduler"



mkdir -p $simulated_files_dir

echoinred "==== RUNNING SIMULATIONS ===="

for f in $input_files
do
	for sched in $algos
	do
		#./run_simulator.py --num-processors=42 --input-file=sample_input --scheduler=EasyBackfillScheduler --output-swf=dada.swf
		fshort=$(basename -s .swf "$f")
		echoinblue ./pyss/src/run_simulator.py --input-file="$f" --scheduler="$sched" --output-swf="$simulated_files_dir/${fshort}_${sched}.swf"
		./pyss/src/run_simulator.py --input-file="$f" --scheduler="$sched" --output-swf="$simulated_files_dir/${fshort}_${sched}.swf"
	done
done


echoinred "==== RUNNING ANALYSIS ===="
echoinblue Rscript simul_analysis.R $final_csv_file $simulated_files_dir/*.swf
Rscript simul_analysis.R $final_csv_file $simulated_files_dir/*.swf


echoinred "==== THE END. Results are in results.csv ===="


