import os
import shutil
import subprocess
from pathlib import Path

import typer

import aviary.api as av

app = typer.Typer(add_completion=False)
_REPO_ROOT = Path(__file__).parent.parent
SIM_DIR_ROOT = Path(_REPO_ROOT, "simulations")


# Results:
# Demo
#   Optimise Mach
#       Total fuel burn: 10649.878199864977 kg (poly=1)
#       Total fuel burn: 10396.216439003885 kg (poly=3)
#       Total fuel burn: 5867.309128890801 kg (poly=1, range = 0.5x)
# Drawn
#   Optimise Mach
#       Total fuel burn: 11460.60343958433 kg (FwFm, AR=11.22)
#       Total fuel burn: 9844.338389973429 kg (AR=15)
#   Not optimised Mach
#       Total fuel burn: 11467.727080250714 kg (FwFm (AR=11.22))
#       Total fuel burn: 10165.515311373754 kg (AR = 15)
#
# ------------------------
# run test --no-optimise-mach                               // No optimisation
#   Total fuel burn: 10671.588549088012 kg
#
# run test                                                  // Optimise Mach only
#   Total fuel burn: 10649.69593342854 kg
#
# run test --optimise-altitude --no-optimise-mach           //Optimise altitude only
#   Total fuel burn: 10638.557638017872 kg
#
# run test --optimise-altitude                              // Optimise Mach and alt
#   Total fuel burn: 10625.736305195798 kg
#
# run test --optimise-altitude --optimsiation-order 2       // Optimise Mach and alt, order=2
#   Total fuel burn: 10337.833343910841 kg
#
# run test --optimise-altitude --optimsiation-order 3       // Optimise Mach and alt, order=3
# ## NOT CONVERGED (within 500 it) ##
#   Total fuel burn: 10319.30178236767 kg
#
#
# run test --no-use-demo-phases
#   Total fuel burn: 11305.379921054335 kg
#
# -------------------------------------------
# Level 2 optimisation - aircraft and mission
#
# AR up to 14:
#   Total fuel burn: 9852.947327704178 kg
#   Aspect ratio: 13.99999820514286
#
# AR up to 14 & 1200 < Area < 1400 ft**2
#   Total fuel burn: 9599.173191455042 kg
#   Aspect ratio: 13.999997565684794
#
#
#   Total fuel burn: 9587.997833642354 kg
#   Aspect ratio: 13.999997636982718
#   Wing Area: 1499.999751035476 ft**2
#   Wing Sweep: 17.39934607170123 deg
#
#
#
#   Total fuel burn: 9587.997833642868 kg
#   Aspect ratio: 13.99999763698272
#   Wing Area: 1499.999751035476 ft**2
#   Wing Sweep: 17.39934633231993 deg
#   Taper ratio: 0.27812412979814777        # Optimal was unchanged (apparently) - perhaps overconstrained elsewhere?
#
#
#   Total fuel burn: 9296.87365331673 kg
#   Aspect ratio: 13.999997619480911
#   Wing Area: 1499.999757249864 ft**2
#   Wing Sweep: 15.000233572764584 deg
#   Taper ratio: 0.278162026834695
#   Thickness-to-chord: 0.10000004626313237
#
#
#
#   Total fuel burn: 7785.696681207821 kg.
#   fuel_burned: 17164.523030243698
#   mission:design:gross_mass: 157500.14177407598. Limits: (100000.0,200000.0)
#   aircraft:wing:aspect_ratio: 13.999995383186302. Limits: (10.0,13.999999999999998)
#   aircraft:wing:area: 2499.999153845772. Limits: (1200.0,2500.0)
#   aircraft:wing:sweep: -5.09855663176955. Limits: (-15.0,40.0)
#   aircraft:wing:taper_ratio: 0.25537628047078265. Limits: (0.0,0.5)
#   aircraft:wing:thickness_to_chord: 0.0100158516903117. Limits: (0.0,0.16000000000000003)


def get_phase_info(
    use_demo_phases=True,
    optimise_mach=True,
    optimise_altitude=False,
    optimsiation_order=1,
    range_multiplier=1,
):
    simple_mission = {
        "pre_mission": {"include_takeoff": False, "optimize_mass": True},
        "climb_1": {
            "subsystem_options": {"core_aerodynamics": {"method": "computed"}},
            "user_options": {
                "optimize_mach": False,
                "optimize_altitude": False,
                "polynomial_control_order": 1,
                "num_segments": 2,
                "order": 3,
                "solve_for_range": False,
                "initial_mach": (0.2, "unitless"),
                "final_mach": (0.72, "unitless"),
                "mach_bounds": ((0.18, 0.74), "unitless"),
                "initial_altitude": (0.0, "ft"),
                "final_altitude": (30500.0, "ft"),
                "altitude_bounds": ((0.0, 31000.0), "ft"),
                "throttle_enforcement": "path_constraint",
                "fix_initial": True,
                "constrain_final": False,
                "fix_duration": False,
                "initial_bounds": ((0.0, 0.0), "min"),
                "duration_bounds": ((27.0, 81.0), "min"),
            },
            "initial_guesses": {"times": ([0, 54], "min")},
        },
        "cruise": {
            "subsystem_options": {"core_aerodynamics": {"method": "computed"}},
            "user_options": {
                "optimize_mach": False,
                "optimize_altitude": False,
                "polynomial_control_order": 1,
                "num_segments": 2,
                "order": 3,
                "solve_for_range": False,
                "initial_mach": (0.72, "unitless"),
                "final_mach": (0.72, "unitless"),
                "mach_bounds": ((0.7, 0.74), "unitless"),
                "initial_altitude": (30500.0, "ft"),
                "final_altitude": (31000.0, "ft"),
                "altitude_bounds": ((30000.0, 31500.0), "ft"),
                "throttle_enforcement": "boundary_constraint",
                "fix_initial": False,
                "constrain_final": False,
                "fix_duration": False,
                "initial_bounds": ((27.0, 81.0), "min"),
                "duration_bounds": ((85.5, 256.5), "min"),
            },
            "initial_guesses": {"times": ([54, 171], "min")},
        },
        "descent_1": {
            "subsystem_options": {"core_aerodynamics": {"method": "computed"}},
            "user_options": {
                "optimize_mach": False,
                "optimize_altitude": False,
                "polynomial_control_order": 1,
                "num_segments": 2,
                "order": 3,
                "solve_for_range": False,
                "initial_mach": (0.72, "unitless"),
                "final_mach": (0.2, "unitless"),
                "mach_bounds": ((0.18, 0.74), "unitless"),
                "initial_altitude": (31000.0, "ft"),
                "final_altitude": (500.0, "ft"),
                "altitude_bounds": ((0.0, 31500.0), "ft"),
                "throttle_enforcement": "path_constraint",
                "fix_initial": False,
                "constrain_final": True,
                "fix_duration": False,
                "initial_bounds": ((112.5, 337.5), "min"),
                "duration_bounds": ((26.5, 79.5), "min"),
            },
            "initial_guesses": {"times": ([225, 53], "min")},
        },
        "post_mission": {
            "include_landing": False,
            "constrain_range": True,
            "target_range": (1915, "nmi"),
        },
    }

    simple_mission_drawn = {
        "pre_mission": {"include_takeoff": False, "optimize_mass": True},
        "climb_1": {
            "subsystem_options": {"core_aerodynamics": {"method": "computed"}},
            "user_options": {
                "optimize_mach": False,
                "optimize_altitude": False,
                "polynomial_control_order": 1,
                "num_segments": 2,
                "order": 3,
                "solve_for_range": False,
                "initial_mach": (0.2, "unitless"),
                "final_mach": (0.72, "unitless"),
                "mach_bounds": ((0.18000000000000002, 0.74), "unitless"),
                "initial_altitude": (0.0, "ft"),
                "final_altitude": (33000.0, "ft"),
                "altitude_bounds": ((0.0, 33500.0), "ft"),
                "throttle_enforcement": "path_constraint",
                "fix_initial": True,
                "constrain_final": False,
                "fix_duration": False,
                "initial_bounds": ((0.0, 0.0), "min"),
                "duration_bounds": ((55.5, 166.5), "min"),
            },
            "initial_guesses": {"times": ([0, 111], "min")},
        },
        "cruise_1": {
            "subsystem_options": {"core_aerodynamics": {"method": "computed"}},
            "user_options": {
                "optimize_mach": False,
                "optimize_altitude": False,
                "polynomial_control_order": 1,
                "num_segments": 2,
                "order": 3,
                "solve_for_range": False,
                "initial_mach": (0.72, "unitless"),
                "final_mach": (0.72, "unitless"),
                "mach_bounds": ((0.7, 0.74), "unitless"),
                "initial_altitude": (33000.0, "ft"),
                "final_altitude": (33000.0, "ft"),
                "altitude_bounds": ((32500.0, 33500.0), "ft"),
                "throttle_enforcement": "boundary_constraint",
                "fix_initial": False,
                "constrain_final": False,
                "fix_duration": False,
                "initial_bounds": ((55.5, 166.5), "min"),
                "duration_bounds": ((70.5, 211.5), "min"),
            },
            "initial_guesses": {"times": ([111, 141], "min")},
        },
        "descent_1": {
            "subsystem_options": {"core_aerodynamics": {"method": "computed"}},
            "user_options": {
                "optimize_mach": False,
                "optimize_altitude": False,
                "polynomial_control_order": 1,
                "num_segments": 2,
                "order": 3,
                "solve_for_range": False,
                "initial_mach": (0.72, "unitless"),
                "final_mach": (0.2, "unitless"),
                "mach_bounds": ((0.18000000000000002, 0.74), "unitless"),
                "initial_altitude": (33000.0, "ft"),
                "final_altitude": (0.0, "ft"),
                "altitude_bounds": ((0.0, 33500.0), "ft"),
                "throttle_enforcement": "path_constraint",
                "fix_initial": False,
                "constrain_final": True,
                "fix_duration": False,
                "initial_bounds": ((126.0, 378.0), "min"),
                "duration_bounds": ((32.5, 97.5), "min"),
            },
            "initial_guesses": {"times": ([252, 65], "min")},
        },
        "post_mission": {
            "include_landing": False,
            "constrain_range": True,
            "target_range": (2028, "nmi"),
        },
    }

    if use_demo_phases:
        phase_info = simple_mission
    else:
        phase_info = simple_mission_drawn

    def _is_mission_segment(phase: str) -> bool:
        return (
            str(phase).startswith("cruise")
            or str(phase).startswith("climb")
            or str(phase).startswith("desc")
        )

    if optimise_mach:
        for phase in phase_info:
            if _is_mission_segment(phase):
                phase_info[phase]["user_options"]["optimize_mach"] = True

    if optimise_altitude:
        for phase in phase_info:
            if _is_mission_segment(phase):
                phase_info[phase]["user_options"]["optimize_altitude"] = True

    if optimsiation_order > 1:
        for phase in phase_info:
            if _is_mission_segment(phase):
                phase_info[phase]["user_options"]["polynomial_control_order"] = optimsiation_order

    phase_info["post_mission"]["target_range"] = (
        phase_info["post_mission"]["target_range"][0] * range_multiplier,
        phase_info["post_mission"]["target_range"][1],
    )
    return phase_info


def _get_sim_dir(sim_name: str) -> Path:
    return Path(SIM_DIR_ROOT, sim_name)


def _get_target_aircraft_and_phases_files(sim_name: str) -> Path:
    sim_dir = _get_sim_dir(sim_name)
    ac_file = Path(sim_dir, f"{sim_name}_aircraft.csv")
    # This is the required filename as it's hard-coded for now in aviary
    mp_file = Path(sim_dir, f"outputted_phase_info.py")
    # mp_file = Path(sim_dir, f"{sim_name}_phases.py")
    return ac_file, mp_file


@app.command()
def init(
    sim_name: str,
    overwrite: bool = False,
    source_aircraft_file: Path = Path(
        _REPO_ROOT, "aviary", "models", "test_aircraft", "aircraft_for_bench_FwFm.csv"
    ),
    source_mission_phases_file: Path = Path(
        _REPO_ROOT, "aviary", "interface", "default_phase_info", "gasp.py"
    ),
) -> None:
    print(f"{sim_name}")
    sim_dir = _get_sim_dir(sim_name)
    print(f"Creating the necessary files for a sim with name: {sim_name} in {sim_dir}")
    if sim_dir.exists():
        if not overwrite:
            raise ValueError(
                "A sim with this name already exists. "
                "Choose another name or pass the --overwrite flag.\n"
                # "Use `ha_helper.py run sim_name` to run the simulation."
            )
    else:
        print("Making sim dir")
        sim_dir.mkdir(parents=True, exist_ok=True)
    # Get copies of the mission and aircraft files that can be edited
    target_aircraft_file, target_mission_phases_file = _get_target_aircraft_and_phases_files(
        sim_name
    )
    os.chdir(sim_dir)
    if source_aircraft_file.exists():
        shutil.copyfile(source_aircraft_file, target_aircraft_file)
    else:
        raise ValueError(f"Given source aircraft .csv ({source_aircraft_file}) doesn't exist!")
    if source_mission_phases_file.exists():
        shutil.copyfile(source_mission_phases_file, target_mission_phases_file)
    else:
        raise ValueError(
            f"Given source mission_phases.py ({source_mission_phases_file}) doesn't exist!"
        )


@app.command()
def run(
    sim_name: str,
    mission_method: str = "simple",
    flops_or_gasp: str = "FLOPS",
    use_demo_phases: bool = True,
    optimise_mach: bool = True,
    optimise_altitude: bool = False,
    optimsiation_order: int = 1,
    range_multiplier: float = 1,
    max_iter: int = 500,
    optimizer: str = "IPOPT",
) -> None:
    sim_dir = _get_sim_dir(sim_name)
    print(f"Simdir: {sim_dir}")
    os.chdir(sim_dir)
    aircraft_filename, mission_phases_file = _get_target_aircraft_and_phases_files(sim_name)

    phase_info = get_phase_info(
        use_demo_phases,
        optimise_mach,
        optimise_altitude,
        optimsiation_order,
        range_multiplier,
    )

    # TODO: Calculate according to whether we need to adjust some design vars
    runlevel = 2

    if runlevel == 1:
        prob = av.run_aviary(
            aircraft_filename,
            phase_info,
            mission_method=mission_method,
            mass_method=flops_or_gasp,
            optimizer=optimizer,
            make_plots=True,
            max_iter=max_iter,
        )
    elif runlevel == 2:
        prob = av.AviaryProblem(
            phase_info, mission_method, flops_or_gasp, av.AnalysisScheme.COLLOCATION
        )

        # Load aircraft and options data from user
        # Allow for user overrides here
        prob.load_inputs(aircraft_filename)

        # Have checks for clashing user inputs
        # Raise warnings or errors depending on how clashing the issues are
        prob.check_inputs()
        prob.add_pre_mission_systems()
        prob.add_phases()
        prob.add_post_mission_systems()

        # Link phases and variables
        prob.link_phases()
        prob.add_driver(optimizer, max_iter=max_iter)
        prob.add_design_variables()

        # Add the Aircraft variables that we'd like to optimise over
        # prob.model.add_design_var(av.Aircraft.Engine.SCALED_SLS_THRUST, lower=25.e3, upper=30.e3, units='lbf', ref=28.e3)
        prob.model.add_design_var(av.Aircraft.Wing.ASPECT_RATIO, lower=10.0, upper=14.0, ref=12.0)
        prob.model.add_design_var(
            av.Aircraft.Wing.AREA, lower=1200.0, upper=2500.0, ref=1370.0, units="ft**2"
        )
        prob.model.add_design_var(av.Aircraft.Wing.SWEEP, lower=-15, upper=40, ref=25, units="deg")
        prob.model.add_design_var(av.Aircraft.Wing.TAPER_RATIO, lower=0.0, upper=0.5, ref=0.278)
        prob.model.add_design_var(
            av.Aircraft.Wing.THICKNESS_TO_CHORD, lower=0.0, upper=0.16, ref=0.1
        )
        # prob.model.add_design_var(    # Doesn't appear to have any influence on the results
        #     av.Mission.Design.RANGE, lower=1500, upper=5500, ref=3500, units="nm"
        # )

        # Load optimization problem formulation
        # Detail which variables the optimizer can control
        prob.add_objective()
        prob.setup()
        prob.set_initial_guesses()

        prob.run_aviary_problem(make_plots=True)

    optimised_mission_optimised_wing_fuel_burn = prob.get_val("fuel_burned", units="kg")[0]
    print(f"Total fuel burn: {optimised_mission_optimised_wing_fuel_burn} kg.")
    # Need to pull out the values in the proper units (which don't seem to be stored anywhere useful) before we can use this generic print statement
    # for o in prob.model.get_objectives().values():
    #     print(f"{o['name']}: {prob.get_val(o['name'])[0]}")

    for v in prob.model._design_vars.values():
        print(
            f"{v['name']}: {prob.get_val(v['name'])[0]}. Limits: ({v['lower']*v['ref']},{v['upper']*v['ref']})"
        )


if __name__ == "__main__":
    app()
