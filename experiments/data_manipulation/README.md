The tree for a log file workflow should be this one at inception:

.
├── Makefile
├── analysis_results
├── original_swf
│   └── log_unfiltered.swf
├── predicted_swf
├── prediction_results
└── simulated_swf

the name of the log (log_unfiltered.swf) is mandatory.
/!\ the Makefile should be modified to contain variables:
 - max_runtime
 - mak_procs

then,when running make filter:

.
├── Makefile
├── analysis_results
├── original_swf
│   ├── log_unfiltered.swf
│   └── log.swf
├── predicted_swf
├── prediction_results
└── simulated_swf

then, when running make extract:
the extracted features are generated.

.
├── Makefile
├── analysis_results
├── original_swf
│   ├── extracted_features
│   ├── log_unfiltered.swf
│   └── log.swf
├── predicted_swf
├── prediction_results
└── simulated_swf

then, with make predict:

.
├── Makefile
├── analysis_results
├── original_swf
│   ├── extracted_features
│   ├── log_unfiltered.swf
│   └── log.swf
├── predicted_swf
├── prediction_results
│   ├── prediction_method1
│   └── prediction_method2
└── simulated_swf

the names of the prediction results can be anything.

then, with make swfs:

.
├── Makefile
├── analysis_results
├── original_swf
│   ├── extracted_features
│   ├── log_unfiltered.swf
│   └── log.swf
├── predicted_swf
│   ├── prediction_method1.swf
│   └── prediction_method2.swf
├── prediction_results
│   ├── prediction_method1
│   └── prediction_method2
└── simulated_swf

then, with make simulate:

.
├── Makefile
├── analysis_results
├── original_swf
│   ├── extracted_features
│   ├── log_unfiltered.swf
│   └── log.swf
├── predicted_swf
│   ├── prediction_method1.swf
│   └── prediction_method2.swf
├── prediction_results
│   ├── prediction_method1
│   └── prediction_method2
└── simulated_swf
    ├── prediction_method1_algo1.swf
    ├── prediction_method1_algo2.swf
    ├── prediction_method2_algo1.swf
    └── prediction_method2_algo2.swf
