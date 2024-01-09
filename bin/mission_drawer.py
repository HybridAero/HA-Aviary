from dataclasses import dataclass

import plotly.graph_objects as go
from plotly.subplots import SubplotXY, make_subplots


@dataclass
class MissionProfile:
    mission_dict: dict

    def plot(self):
        fig = make_subplots(
            1,
            2,
            subplot_titles=("Mach Profile", "Altitude Profile"),
            # horizontal_spacing=0.05,
            # vertical_spacing=0.1,
        )
        time_nominal = []
        time_errors_lwr = []
        time_errors_upr = []
        mach_nominal = []
        alt_nominal = []
        mach_box = []
        alt_box = []
        for phase_name in self.mission_dict:
            if phase_name == "pre_mission" or phase_name == "post_mission":
                continue
            phase_data = self.mission_dict[phase_name]["user_options"]
            t_init_guess, duration_init_guess = self.mission_dict[phase_name]["initial_guesses"][
                "times"
            ][0]
            m_min, m_max = phase_data["mach_bounds"][0]
            a_min, a_max = phase_data["altitude_bounds"][0]
            time_nominal.append(t_init_guess)
            time_errors_lwr.append(t_init_guess - phase_data["initial_bounds"][0][0])
            time_errors_upr.append(phase_data["initial_bounds"][0][1] - t_init_guess)
            mach_nominal.append(phase_data["initial_mach"][0])
            alt_nominal.append(phase_data["initial_altitude"][0])
            mach_box.append((t_init_guess, t_init_guess + duration_init_guess, m_min, m_max))
            alt_box.append((t_init_guess, t_init_guess + duration_init_guess, a_min, a_max))
        # Need to add the final ones too
        time_nominal.append(t_init_guess + duration_init_guess)
        time_errors_lwr.append(
            time_nominal[-1]
            - (phase_data["initial_bounds"][0][0] + phase_data["duration_bounds"][0][0])
        )
        time_errors_upr.append(
            (phase_data["initial_bounds"][0][1] + phase_data["duration_bounds"][0][1])
            - time_nominal[-1]
        )

        mach_nominal.append(phase_data["final_mach"][0])
        alt_nominal.append(phase_data["final_altitude"][0])

        # Draw shaded boxes of the available region (draw these first so they're 'behind' the traces)
        range_boxes_colour = "rgba(50, 50, 255, 0.25)"
        show_mach_legend = True
        for box in mach_box:
            # bl, br, tr, tl
            xs = [box[0], box[1], box[1], box[0]]
            ys = [box[2], box[2], box[3], box[3]]
            fig.add_trace(
                go.Scatter(
                    x=xs,
                    y=ys,
                    fill="toself",
                    fillcolor=range_boxes_colour,
                    mode="none",
                    name="Permissible Mach Range",
                    legendgroup="machrange",
                    showlegend=show_mach_legend,
                ),
                row=1,
                col=1,
            )
            show_mach_legend = False
        show_alt_legend = True
        for box in alt_box:
            # bl, br, tr, tl
            xs = [box[0], box[1], box[1], box[0]]
            ys = [box[2], box[2], box[3], box[3]]
            fig.add_trace(
                go.Scatter(
                    x=xs,
                    y=ys,
                    fill="toself",
                    fillcolor=range_boxes_colour,
                    mode="none",
                    name="Permissible Altitude Range",
                    legendgroup="altrange",
                    showlegend=show_alt_legend,
                ),
                row=1,
                col=2,
            )
            show_alt_legend = False

        #  Error bars for the X location (i.e. time range for each phase)
        fig.add_trace(
            go.Scatter(
                x=time_nominal,
                y=mach_nominal,
                mode="lines",
                line_shape="linear",
                name="Time Range",
                line={"color": "blue"},
                opacity=0.5,
                error_x=dict(
                    type="data",
                    symmetric=False,
                    color="blue",
                    array=time_errors_upr,
                    arrayminus=time_errors_lwr,
                ),
                legendgroup="timeerror",
                legendrank=20,
                showlegend=True,
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=time_nominal,
                y=alt_nominal,
                mode="lines+markers",
                line_shape="linear",
                name="Time Range",
                line={"color": "blue"},
                opacity=0.5,
                error_x=dict(
                    type="data",
                    symmetric=False,
                    color="blue",
                    array=time_errors_upr,
                    arrayminus=time_errors_lwr,
                ),
                legendgroup="timeerror",
                showlegend=False,
            ),
            row=1,
            col=2,
        )

        # Main traces
        fig.add_trace(
            go.Scatter(
                x=time_nominal,
                y=mach_nominal,
                mode="lines+markers",
                line_shape="linear",
                name="Nominal Profile",
                line={"color": "blue"},
                legendgroup="nominal",
                legendrank=10,  # Puts the 'Nominal Profile' at the top of the legend order
                showlegend=True,
                # hovertemplate=(
                #     '<span style="text-decoration: underline; text-align: center"><b>%{text}</b><br></span>'
                #     f"<b>{x_label_clean}</b>: " + "%{x}<br>"
                #     f"<b>{y_label_clean}</b>: " + "%{y:.4f}"
                # ),
                # text=this_legend_df.index,
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=time_nominal,
                y=alt_nominal,
                mode="lines+markers",
                line_shape="linear",
                name="Nominal Profile",
                line={"color": "blue"},
                legendgroup="nominal",
                showlegend=False,
            ),
            row=1,
            col=2,
        )

        fig["layout"]["xaxis"]["title"] = "Time (min)"
        fig["layout"]["xaxis2"]["title"] = "Time (min)"
        fig["layout"]["yaxis"]["title"] = "Mach #"
        fig["layout"]["yaxis2"]["title"] = "Altitude (ft)"
        fig.layout["yaxis"]["rangemode"] = "tozero"
        fig.layout["yaxis2"]["rangemode"] = "tozero"
        fig.update_layout(
            title_text="Mission Profile",
        )
        fig.show()
