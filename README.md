# HAviary -- HybridAero's version of NASA's aircraft design tool

## Usage
Note that `Aviary` very much appears geared for Linux, but seems to just about work on Windows

### Build a mission
Only required if you wish to specify a new mission, otherwise use an example one.  
```
aviary draw_mission
```
Opens a GUI that lets you click some points to build an Altitude/Mach vs time plot for the mission.
Also lets you select which segments can be optimised for Mach/Altitude.
The file will be saved to `outputted_phase_info.py` in your current working directory, so move this to the appropriate simulation directory once it's finished.  
Note that you might need to `ctrl-C` to get it to close properly. (if `ctrl-C` doesn't work, try `ctrl-Break` (which on a Logitech keyboard is `ctrl-fn-b`))

The mission drawer will solve for the expected range given the time specified at each altitude/Mach.  
Aviary's main optimisation strategy is to alter the duration of each segment such that the total mission range is achieved.

Further to altering the duration, it can optimise for Mach and altitude during each stage. The order of fit can range from linear (order=1) up to cubic (order=3) (or potentially beyond - not yet tested)



Also note that some 'mission' parameters are also found in the `aircraft.csv` file!

### Level 1 usage
Optimise the mission altitude/Mach to minimise fuel burn. (The only type of optimisation supported for level 1 usage)

#### Initialisation
```
python .\bin\ha_helper.py init <sim_name>
```
will create copies of the required `aircraft.csv` and `mission_phase.py` files, which is all you need to define the simulation.  
You can either edit an existing `mission_phase.py` file, or use the mission builder to create a new file for you ([see below](#build-a-mission)).
You can also specify the full path to an example aircraft file if you don't want to use the default.

#### Simulating
``` 
.\bin\ha_helper.py run <sim_name>
``` 
will print the aviary command that you need to copy/paste to execute to run the simulation. (The entry point isn't very friendly for Level 1 use, which is why this just prints the command instead of running it for you...)

### Define an aircraft
Take a copy of one of NASA's example aircrafts to get started, then modify the values.  

### Run a simulation
```
aviary run_mission $aircraft_file --optimizer IPOPT --max_iter 100 --mass_origin GASP --mission_method GASP --phase_info $mission_phases_file -o $output_directory
```

## Background
### [Options/Arguments](https://openmdao.github.io/om-Aviary/getting_started/onboarding_level1.html#level-1-run-options)
Optimisation objective is **always** fuel-burn in level 1  
Important options:  

- `--phase_info`
  - This is how to specify the mission _phases_
    - Requires a path to a `phases.py` file
      - Broken in the code, if not `None`, then it looks for a file called `outputted_phase_info.py` in the current working directory...
    - If not specified, it uses `interface/default_phase_info/flops.py` or `interface/default_phase_info/gasp.py` as appropriate
- `--mission_method`  
  - Missions can either by run as `simple`, `FLOPS` or `GASP`. 
  - `simple` is the default and [apparently recommended](https://openmdao.github.io/om-Aviary/examples/simple_mission_example.html#how-to-define-an-aircraft:~:text=We%20strongly%20suggest%20using%20the%20simple%20mission%20method%20as%20it%20is%20the%20most%20robust%20and%20easiest%20to%20use) as the most robust/stable.
    - It's unfortunate therefore that the 'simple' example they provide doesn't actually work, so we'll use GASP in the meantime
- `--mass_origin`
  - `FLOPS` or `GASP`
- `--outdir`
  - Where to write the results to (this seems to be ignored at the moment...)

### FLOPS
`Flight Optimization System` [comprises the following modules](https://openmdao.github.io/om-Aviary/getting_started/tools_that_aviary_uses.html#flops):  
1. Weights
  - Statistical/Empirical equations used to predict component weights
1. Aerodynamics
  - provides lift/drag polars, or drag polars can be supplied and scaled with variations in wing area/nacelle size
1. Propulsion data scaling & interpolation
  - Requires an input engine deck, then scales to desired thrust
1. Mission Performance
    - Uses weights/aero/propulsion to do energy-balance calculations.
    - Can include segments:
      - Climb
      - Cruise
      - Descent
      - Reserve
        - Flight to alternative airport or hold
1. Take-off & Landing
  - All-engine take-off field length
  - BFL (inc OEI/aborted take-off)
  - Landing field length
    - Approach speed
1. Program Control
  - Point design analysis
  - Parametric design variable sensitivity
  - Configuration optimisation
    - Objectives
      - Min fuel usage
      - Max range
      - Min NOx emissions
    - Input options (apparently)
      - Design variables for
        - Aircraft configuration
        - Performance

### GASP
`General Aviation Synthesis Program`
Apparently allows rapid parametric study for preliminary design.  
From their description:
- Contains modules representing 'various technical disciplines' integrated into a computational flow which ensures that the interacting effects of design variables are continuously accounted for in the aircraft sizing procedure
- Useful for 
  - comparing configurations
  - assessing performance and economics
  - performing trade-off and sensitivity studies
  - assessing the impact of advanced technologies on aircraft performance and economics
- Supplies a systematic method for investigating requirements/design factors, always measured in terms of overall aircraft performance/economics



# Nasa's README below:

## Description

This repository is an [OpenMDAO](https://openmdao.org/)-based aircraft modeling tool that incorporates aircraft sizing and weight equations from its predecessors [GASP (General Aviation Synthesis Program)](https://ntrs.nasa.gov/api/citations/19810010563/downloads/19810010563.pdf) and [FLOPS (Flight Optimization System)](https://software.nasa.gov/software/LAR-18934-1).
It also incorporates aerodynamic calculations from GASP and FLOPS and has the capability to use an aerodynamics deck as well as an aircraft engine deck.
There are two options for the mission analysis portion of this code, a 2 degrees-of-freedom (2DOF) approach, and a height energy (HtEn) approach.
The user can select which type of mission analysis to use, as well as whether to use the FLOPS-based code or the GASP-based code for the weight, sizing, and aerodynamic relations.

## Installation

The simplest installation method for development is an "editable mode" install with ``pip`` in your terminal:

    pip install -e .

This installs the package in the current environment such that changes to the Python code don't require re-installation.This command should be performed while in the folder containing ``setup.py``.

## Documentation

The Aviary documentation is located [here](https://openmdao.github.io/om-Aviary/intro.html).

Otherwise you can build the docs locally:

1. Install jupyter-book using instructions located [here](https://jupyterbook.org/en/stable/start/overview.html
)
2. Go to Aviary/aviary/docs
3. Run the command `sh build_book.sh` from your command prompt of choice
4. Navigate to the built html: `/Aviary/aviary/docs/\_build/html/intro.html`

## Visualization

To visualize XDSMs and successfully pass spec tests, all the XDSM files must be run. This can be done using the `run_all.py` utility script within the `aviary/xdsm` directory. This is a necessary step before unit testing, otherwise unit tests will fail.

## Validation

This code has been validated using output and data from the GASP and FLOPS codes themselves. The GASP-based weight calculations in this code include in their comments which versions of the GASP standalone weights module were used in validation. The aero and EOM subsystem validations were based on runs of the entire GASP and FLOPS code as they stood in the summer of 2021 and the summer of 2022 respectively.

### Quick testing

The repository installation can be tested using the command ``testflo .`` at the top-level Aviary folder. Assuming you have both SNOPT and IPOPT installed, the output should look something like this:

        OK

        Passed:  706
        Failed:  0
        Skipped: 3


        Ran 709 tests using 16 processes
        Wall clock time:   00:00:16.97

### Full testing

In addition to all of the quicker tests, we include multiple integration tests within Aviary.
These have also been known as "benchmarks".
Due to their length, these tests are not run when using the above command.
Instead, you can use the `run_all_benchmarks.py` file in the `Aviary/aviary` folder, which is just a light wrapper around the `testflo` call.
This will run all of the longer tests in parallel using all of your available CPU cores.

## Package Versions

Information on the versions of the packages required for Aviary can be found in the most recent [GitHub Actions runs](https://github.com/OpenMDAO/Aviary/actions).
We have also provided a static version of the `environment.yml` at the top level of the Aviary repo.