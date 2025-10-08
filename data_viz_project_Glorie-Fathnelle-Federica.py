#!/usr/bin/env python
"""
Interactive Presentation App with Bokeh
Run with: bokeh serve presentation.py
Then open: http://localhost:5006/presentation
"""

# === CORE IMPORTS ===
import os
import numpy as np
import pandas as pd
from bokeh.plotting import figure, curdoc

from bokeh.models import (
    Div, Button, Select, ColumnDataSource, HoverTool,
    Range1d, LinearAxis, LinearColorMapper, ColorBar, CustomJS
)
from bokeh.layouts import column, row, layout
from bokeh.palettes import YlOrRd9
from bokeh.transform import linear_cmap, factor_cmap, dodge
from bokeh.events import DocumentReady


class InteractivePresentation:
    """Main application class for the Bokeh presentation system."""

    def __init__(self):
        self.current_slide = 0
        self.slides = []
        self.auto_play = False
        self.auto_play_callback = None
        
        # Load data once
        self.df = None
        self.csv_path = os.path.join(os.path.dirname(__file__), "student_lifestyle_dataset.csv")
        self._load_data()
        
        # Create presentation
        self.create_slides()
        self.total_slides = len(self.slides)
        self.create_navigation()
        self.create_layout()

    def _load_data(self):
        """Load CSV once at startup."""
        try:
            self.df = pd.read_csv(self.csv_path)
        except Exception as e:
            print(f"[ERROR] Cannot read {self.csv_path}: {e}")
            self.df = None

    # === NAVIGATION ===
    def create_navigation(self):
        """Create navigation controls"""
        self.prev_button = Button(label="◀ Previous", button_type="primary", width=100)
        self.next_button = Button(label="Next ▶", button_type="primary", width=100)
        self.home_button = Button(label="🏠 Home", button_type="warning", width=100)
        self.play_button = Button(label="▶ Auto Play", button_type="success", width=100)
        self.stop_button = Button(label="⏸ Stop", button_type="danger", width=100)
        
        slide_options = [(str(i), f"Slide {i + 1}: {self.get_slide_title(i)}") 
                        for i in range(self.total_slides)]
        self.slide_select = Select(title="Jump to:", value="0", options=slide_options, width=300)
        self.progress_div = Div(text=self.get_progress_html(), width=200)
        
        # Attach callbacks
        self.prev_button.on_click(self.prev_slide)
        self.next_button.on_click(self.next_slide)
        self.home_button.on_click(self.go_home)
        self.play_button.on_click(self.start_auto_play)
        self.stop_button.on_click(self.stop_auto_play)
        self.slide_select.on_change("value", self.jump_to_slide)

    def get_slide_title(self, index):
        """Get title for each slide"""
        titles = [
            "Welcome & Introduction",
            "GPA vs Study Hours (by Stress)",
            "GPA & Stress by Study/Sleep Habits",
            "Activity Hours by Stress (High Study/Sleep)",
            "Activity Hours - Interactive Filters"
        ]
        return titles[index] if index < len(titles) else f"Slide {index + 1}"

    def get_progress_html(self):
        """Generate progress bar HTML"""
        progress_pct = ((self.current_slide + 1) / self.total_slides) * 100
        return f"""
        <div style="text-align: center;">
            <b>Slide {self.current_slide + 1} of {self.total_slides}</b><br>
            <div style="width: 100%; background-color: #f0f0f0; border-radius: 5px;">
                <div style="width: {progress_pct}%; background-color: #4CAF50; 
                           height: 20px; border-radius: 5px;"></div>
            </div>
        </div>
        """

    # === SLIDES CREATION ===
    def create_slides(self):
        """Create all presentation slides"""
        self.slides = [
            self.create_slide_0_welcome(),
            self.create_slide_1_scatter_gpa_study(),
            self.create_slide_2_gpa_stress_dual_axis(),
            self.create_slide_3_activity_by_stress(),
            self.create_slide_4_activity_interactive()
        ]

    def create_slide_0_welcome(self):
        """Welcome slide with dataset overview and key statistics"""
        title = Div(text="""
            <div style="text-align:center; padding:30px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                       border-radius: 12px; margin-bottom: 25px;">
                <h1 style="margin:0; color:#ffffff; font-size: 42px; font-weight: 700; text-shadow: 2px 2px 4px rgba(0,0,0,0.2);">
                    The Interplay of Lifestyle, Stress Level, and Academic Performance
                </h1>
            </div>
        """, width=1200)
        
        intro = Div(text="""
            <div style="max-width:1100px; margin:0 auto 20px; padding: 25px; background: #ffffff; 
                       border-radius: 12px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                <h2 style="color:#2c3e50; margin-top:0; font-size: 26px; border-bottom: 3px solid #667eea; 
                          padding-bottom: 10px; display: inline-block; margin-bottom: 15px;">
                    Dataset Overview
                </h2>
                <p style="line-height:1.6; font-size:18px; color:#34495e; margin: 0;">
                    This analysis explores the 
                    <b><a href="https://www.kaggle.com/datasets/steve1215rogg/student-lifestyle-dataset" 
                    target="_blank" style="color:#667eea; text-decoration:none; border-bottom: 2px solid #667eea;">
                    Student Lifestyle Dataset</a></b> from Kaggle, containing <b>2,000 student records</b> with information on 
                    <b>study time</b>, <b>sleeping time</b>, <b>physical activities</b>, <b>social activities</b>, 
                    <b>stress levels</b>, and <b>grades</b>.
                </p>
            </div>
        """, width=1200)
        
        stats = Div(text="""
            <div style="max-width:1100px; margin:0 auto;">
                <div style="display: flex; gap: 18px; margin-bottom: 18px;">
                    <div style="flex: 1; background: #ffffff; border-radius: 12px; padding: 25px; 
                               box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                        <h3 style="color:#2c3e50; margin-top:0; font-size: 22px; margin-bottom: 15px;">Stress Distribution</h3>
                        <div style="display:flex; gap:12px; justify-content:space-between;">
                            <div style="flex:1; background: linear-gradient(135deg, #ff6b6b 0%, #c62828 100%); 
                                       border-radius: 10px; padding: 18px; color: white; text-align: center;">
                                <div style="font-size:15px; opacity: 0.9;">High</div>
                                <div style="font-size:38px; font-weight:800; margin: 8px 0;">~50%</div>
                            </div>
                            <div style="flex:1; background: linear-gradient(135deg, #ffa726 0%, #f57c00 100%); 
                                       border-radius: 10px; padding: 18px; color: white; text-align: center;">
                                <div style="font-size:15px; opacity: 0.9;">Moderate</div>
                                <div style="font-size:38px; font-weight:800; margin: 8px 0;">~34%</div>
                            </div>
                            <div style="flex:1; background: linear-gradient(135deg, #66bb6a 0%, #2e7d32 100%); 
                                       border-radius: 10px; padding: 18px; color: white; text-align: center;">
                                <div style="font-size:15px; opacity: 0.9;">Low</div>
                                <div style="font-size:38px; font-weight:800; margin: 8px 0;">~15%</div>
                            </div>
                        </div>
                    </div>
                    
                    <div style="flex: 1; background: #ffffff; border-radius: 12px; padding: 25px; 
                               box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                        <h3 style="color:#2c3e50; margin-top:0; font-size: 22px; margin-bottom: 15px;">Academic Performance</h3>
                        <div style="display:flex; gap:12px;">
                            <div style="flex:1; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                       border-radius: 10px; padding: 18px; color: white; text-align: center;">
                                <div style="font-size:15px; opacity: 0.9;">High Scores</div>
                                <div style="font-size:42px; font-weight:800; margin: 8px 0;">~49%</div>
                                <div style="font-size:13px; opacity: 0.8;">above average</div>
                            </div>
                            <div style="flex:1; background: linear-gradient(135deg, #9575cd 0%, #512da8 100%); 
                                       border-radius: 10px; padding: 18px; color: white; text-align: center;">
                                <div style="font-size:15px; opacity: 0.9;">Lower Scores</div>
                                <div style="font-size:42px; font-weight:800; margin: 8px 0;">~51%</div>
                                <div style="font-size:13px; opacity: 0.8;">below average</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div style="padding: 15px 25px; background: linear-gradient(90deg, #e3f2fd 0%, #f3e5f5 100%); 
                           border-left: 4px solid #667eea; border-radius: 8px;">
                    <p style="margin: 0; font-size: 16px; color: #2c3e50; line-height: 1.6;">
                        <strong style="color: #667eea;">Key Insight:</strong> 
                        Half of students experience high stress; nearly balanced academic performance - understanding lifestyle factors is crucial.
                    </p>
                </div>
            </div>
        """, width=1200)
        
        return layout([[title], [intro], [stats]])

    def create_slide_1_scatter_gpa_study(self):
        """Slide 1: GPA vs Study Hours, colored by Stress Level"""
        if self.df is None:
            return layout([[Div(text="<b>CSV not found.</b>", width=600)]])
        
        df = self.df[["Study_Hours_Per_Day", "GPA", "Stress_Level"]].dropna()
        stress_order = ["Low", "Moderate", "High"]
        stress_palette = ["#2ca02c", "#ff7f0e", "#d62728"]
        df = df[df["Stress_Level"].isin(stress_order)].copy()
        df["Stress_Level"] = pd.Categorical(df["Stress_Level"], categories=stress_order, ordered=True)
        
        source = ColumnDataSource(df)
        
        title = Div(text="""
            <h2 style="text-align:center; color:#2c3e50; font-size: 28px;">
                Academic Performance (GPA) vs. Study Time, Conditioned by Stress
            </h2>
        """, width=900)
        
        p = figure(width=900, height=550, tools="pan,wheel_zoom,box_zoom,reset,save,hover", title=None)
        p.scatter(x="Study_Hours_Per_Day", y="GPA", source=source, size=9, alpha=0.6,
                 color=factor_cmap("Stress_Level", palette=stress_palette, factors=stress_order),
                 legend_field="Stress_Level")
        
        # Formatting
        p.xaxis.axis_label = "Study Hours Per Day"
        p.xaxis.axis_label_text_font_size = "16pt"
        p.xaxis.axis_label_text_font_style = "bold"
        p.xaxis.major_label_text_font_size = "14pt"
        
        p.yaxis.axis_label = "GPA (Grade Point Average)"
        p.yaxis.axis_label_text_font_size = "16pt"
        p.yaxis.axis_label_text_font_style = "bold"
        p.yaxis.major_label_text_font_size = "14pt"
        
        p.legend.title = "Stress Level"
        p.legend.title_text_font_size = "15pt"
        p.legend.title_text_font_style = "bold"
        p.legend.label_text_font_size = "14pt"
        p.legend.location = "top_left"
        p.legend.click_policy = "hide"
        
        p.hover.tooltips = [
            ("Study Hours", "@Study_Hours_Per_Day{0.0}"),
            ("GPA", "@GPA{0.00}"),
            ("Stress Level", "@Stress_Level"),
        ]
        
        return layout([[title], [p]])

    def create_slide_2_gpa_stress_dual_axis(self):
        """Slide 2: Mean GPA vs Mean Stress by Study & Sleep groups (dual y-axis)"""
        if self.df is None:
            return layout([[Div(text="<b>CSV not found.</b>", width=600)]])
        
        df = self.df[["Study_Hours_Per_Day", "Sleep_Hours_Per_Day", "GPA", "Stress_Level"]].dropna()
        
        stress_map = {"Low": 1.0, "Moderate": 2.0, "High": 3.0}
        df["Numeric_Stress"] = df["Stress_Level"].map(stress_map).astype(float)
        
        # Create groups
        median_study = df["Study_Hours_Per_Day"].median()
        median_sleep = df["Sleep_Hours_Per_Day"].median()
        df["Study_Group"] = np.where(df["Study_Hours_Per_Day"] > median_study, "High Study", "Low Study")
        df["Sleep_Group"] = np.where(df["Sleep_Hours_Per_Day"] > median_sleep, "High Sleep", "Low Sleep")
        df["Combined_Group"] = df["Study_Group"] + " & " + df["Sleep_Group"]
        
        group_order = [
            "Low Study & Low Sleep", "Low Study & High Sleep",
            "High Study & Low Sleep", "High Study & High Sleep"
        ]
        
        # Aggregate
        gpa_stress_means = (
            df.groupby("Combined_Group", observed=False)[["GPA", "Numeric_Stress"]]
            .mean().reindex(group_order).reset_index().fillna(0)
        )
        
        # Map stress to categories for dot colors
        def map_stress_category(val):
            if val <= 1.5: return "Low"
            elif val <= 2.5: return "Moderate"
            else: return "High"
        
        gpa_stress_means["Stress_Level_Cat"] = gpa_stress_means["Numeric_Stress"].apply(map_stress_category)
        
        stress_colors = {"Low": "green", "Moderate": "#FFC000", "High": "red"}
        gpa_stress_means["dot_color"] = gpa_stress_means["Stress_Level_Cat"].map(stress_colors)
        
        # GPA size scaling
        gpa_vals = gpa_stress_means['GPA'].values
        gpa_min, gpa_max = float(gpa_vals.min()), float(gpa_vals.max())
        min_size, max_size = 12, 28
        
        if np.isclose(gpa_max, gpa_min):
            sizes = np.full_like(gpa_vals, (min_size + max_size) / 2.0)
        else:
            sizes = (gpa_vals - gpa_min) / (gpa_max - gpa_min) * (max_size - min_size) + min_size
        
        gpa_stress_means["dot_size"] = sizes
        source = ColumnDataSource(gpa_stress_means)
        
        title = Div(text="""
            <h2 style="color:#2c3e50; font-size: 28px;">Mean GPA vs. Mean Stress by Study & Sleep Habits</h2>
            <p style="color:#555; font-size: 16px;">Left axis: Mean GPA | Right axis: Mean Stress (1=Low, 3=High)</p>
        """, width=1100)
        
        p = figure(width=1100, height=550, x_range=group_order, toolbar_location="above",
                  tools="pan,wheel_zoom,box_zoom,reset,save")
        
        # Axes
        p.y_range = Range1d(1, 4)
        p.yaxis.axis_label = "Mean GPA"
        p.yaxis.axis_label_text_color = "#1F77B4"
        p.yaxis.axis_label_text_font_size = "16pt"
        p.yaxis.axis_label_text_font_style = "bold"
        p.yaxis.major_label_text_font_size = "14pt"
        
        p.extra_y_ranges = {"stress": Range1d(start=1, end=4)}
        stress_axis = LinearAxis(y_range_name="stress", axis_label="Mean Stress Score (1=Low, 3=High)",
                                axis_label_text_font_size="16pt", axis_label_text_font_style="bold",
                                major_label_text_font_size="14pt")
        p.add_layout(stress_axis, "right")
        
        # Color palette
        reversed_palette = list(reversed(YlOrRd9))
        color_mapper = LinearColorMapper(palette=reversed_palette, low=1.0, high=4.0)
        
        # Plotting
        bars = p.vbar(x="Combined_Group", top="Numeric_Stress", width=0.6, source=source,
                     line_color="white", fill_color=linear_cmap('Numeric_Stress', reversed_palette, 1.0, 4.0),
                     alpha=0.9, y_range_name="stress", legend_label="Mean Stress")
        
        line = p.line(x="Combined_Group", y="GPA", source=source, line_width=3,
                     color="#1F77B4", legend_label="Mean GPA")
        
        dots = p.circle(x="Combined_Group", y="GPA", size="dot_size", source=source,
                       fill_color="dot_color", line_color="black", line_width=1, alpha=0.7, legend_label="GPA")
        
        # ColorBar
        color_bar = ColorBar(color_mapper=color_mapper, label_standoff=12, border_line_color=None,
                            location=(0, 0), title="Stress Score", title_text_font_size="14pt",
                            major_label_text_font_size="12pt")
        p.add_layout(color_bar, 'right')
        
        # Hover tools
        p.add_tools(HoverTool(renderers=[bars], tooltips=[("Group", "@Combined_Group"), ("Mean Stress", "@Numeric_Stress{0.00}")]))
        p.add_tools(HoverTool(renderers=[dots], tooltips=[("Group", "@Combined_Group"), ("Mean GPA", "@GPA{0.00}"), ("Stress Category", "@Stress_Level_Cat")]))
        
        # Formatting
        p.xaxis.axis_label = "Study & Sleep Habit Group"
        p.xaxis.axis_label_text_font_size = "16pt"
        p.xaxis.axis_label_text_font_style = "bold"
        p.xaxis.major_label_text_font_size = "13pt"
        
        p.legend.location = "top_left"
        p.legend.click_policy = "hide"
        p.legend.label_text_font_size = "13pt"
        p.legend.title_text_font_size = "14pt"
        
        p.xgrid.grid_line_color = None
        p.ygrid.grid_line_dash = "dashed"
        p.ygrid.grid_line_alpha = 0.5
        
        return layout([[title], [p]])

    def create_slide_3_activity_by_stress(self):
        """Slide 3: Activity hours by stress level for high study & high sleep students"""
        if self.df is None:
            return layout([[Div(text="<b>CSV not found.</b>", width=600)]])
        
        df = self.df[["Study_Hours_Per_Day", "Sleep_Hours_Per_Day", "Stress_Level",
                     "Physical_Activity_Hours_Per_Day", "Social_Hours_Per_Day"]].dropna()
        
        stress_map = {'Low': 1.0, 'Moderate': 2.0, 'High': 3.0}
        df['Numeric_Stress'] = df['Stress_Level'].map(stress_map).astype(float)
        
        mean_study = df['Study_Hours_Per_Day'].mean()
        mean_sleep = df['Sleep_Hours_Per_Day'].mean()
        
        df_focus = df[(df['Study_Hours_Per_Day'] > mean_study) & (df['Sleep_Hours_Per_Day'] > mean_sleep)].copy()
        
        stress_order = ['Moderate', 'High', 'Low']
        
        activity_means = df_focus.groupby('Stress_Level')[
            ['Physical_Activity_Hours_Per_Day', 'Social_Hours_Per_Day']
        ].mean().reindex(stress_order).reset_index()
        
        df_melted = pd.melt(activity_means, id_vars=['Stress_Level'],
                           value_vars=['Physical_Activity_Hours_Per_Day', 'Social_Hours_Per_Day'],
                           var_name='Activity Type', value_name='Mean Hours')
        
        df_melted['Activity Type'] = df_melted['Activity Type'].replace({
            'Physical_Activity_Hours_Per_Day': 'Physical Activity',
            'Social_Hours_Per_Day': 'Social Activity'
        })
        
        pivot_data = df_melted.pivot(index='Activity Type', columns='Stress_Level', values='Mean Hours').reindex(stress_order, axis=1).reset_index()
        
        pivot_data['Total'] = pivot_data[stress_order].sum(axis=1)
        pivot_data = pivot_data.sort_values('Total', ascending=False).drop('Total', axis=1)
        
        activity_order = ['Social Activity', 'Physical Activity']
        pivot_data = pivot_data.set_index('Activity Type').reindex(activity_order).reset_index()
        
        stress_colors = {'Low': '#2E7D32', 'Moderate': '#F57C00', 'High': '#C62828'}
        source = ColumnDataSource(pivot_data)
        
        title = Div(text="""
            <h2 style="color:#2c3e50; font-size: 26px; margin-bottom: 5px;">Mean Activity Hours by Stress Level</h2>
            <p style="color:#555; font-size: 18px; margin-top: 5px;">(High Study & High Sleep Students)</p>
        """, width=1000)
        
        note = Div(text="""
            <div style="background-color: #fff3cd; padding: 10px; border-left: 4px solid #ffc107; margin-bottom: 10px; border-radius: 4px;">
                <p style="margin: 0; color: #856404; font-size: 14px;">
                    <strong>Note:</strong> No students in this group reported Low stress levels.
                </p>
            </div>
        """, width=1000)
        
        activity_types = pivot_data['Activity Type'].tolist()
        p = figure(y_range=activity_types, width=1000, height=500, toolbar_location="above",
                  tools="pan,wheel_zoom,box_zoom,reset,save")
        
        dodge_offset = 0.28
        
        bars_high = p.hbar(y=dodge('Activity Type', -dodge_offset, p.y_range), right='High', height=0.22,
                          source=source, color=stress_colors['High'], legend_label='High', alpha=0.85)
        
        bars_moderate = p.hbar(y=dodge('Activity Type', 0, p.y_range), right='Moderate', height=0.22,
                              source=source, color=stress_colors['Moderate'], legend_label='Moderate', alpha=0.85)
        
        bars_low = p.hbar(y=dodge('Activity Type', dodge_offset, p.y_range), right='Low', height=0.22,
                         source=source, color=stress_colors['Low'], legend_label='Low', alpha=0.85)
        
        # Formatting
        p.x_range.start = 0
        p.xaxis.axis_label = "Mean Hours Per Day"
        p.xaxis.axis_label_text_font_size = "18pt"
        p.xaxis.axis_label_text_font_style = "bold"
        p.xaxis.major_label_text_font_size = "15pt"
        
        p.yaxis.axis_label = "Activity Type"
        p.yaxis.axis_label_text_font_size = "18pt"
        p.yaxis.axis_label_text_font_style = "bold"
        p.yaxis.major_label_text_font_size = "16pt"
        
        p.xgrid.grid_line_color = "#e0e0e0"
        p.xgrid.grid_line_dash = "dashed"
        p.ygrid.grid_line_color = None
        
        p.legend.title = "Stress Level"
        p.legend.title_text_font_size = "16pt"
        p.legend.title_text_font_style = "bold"
        p.legend.label_text_font_size = "14pt"
        p.legend.location = "bottom_right"
        p.legend.click_policy = "hide"
        
        # Hover tools
        for bars, label in [(bars_low, 'Low'), (bars_moderate, 'Moderate'), (bars_high, 'High')]:
            p.add_tools(HoverTool(renderers=[bars], tooltips=[
                ("Activity", "@{Activity Type}"),
                ("Stress Level", label),
                ("Mean Hours", f"@{label}{{0.00}}")
            ]))
        
        return layout([[title], [note], [p]])

    def create_slide_4_activity_interactive(self):
        """Slide 4: Interactive activity hours chart with filters"""
        if self.df is None:
            return layout([[Div(text="<b>CSV not found.</b>", width=600)]])
        
        df = self.df.dropna()
        
        # Prepare data
        stress_map = {'Low': 1.0, 'Moderate': 2.0, 'High': 3.0}
        df['Numeric_Stress'] = df['Stress_Level'].map(stress_map).astype(float)
        stress_order = ['Low', 'Moderate', 'High']
        
        # Create groups
        median_study = df["Study_Hours_Per_Day"].median()
        median_sleep = df["Sleep_Hours_Per_Day"].median()
        median_physical = df["Physical_Activity_Hours_Per_Day"].median()
        gpa_threshold = df['GPA'].quantile(0.50)
        
        df["Study_Group"] = np.where(df["Study_Hours_Per_Day"] > median_study, "High Study", "Low Study")
        df["Sleep_Group"] = np.where(df["Sleep_Hours_Per_Day"] > median_sleep, "High Sleep", "Low Sleep")
        df["Combined_Study_Sleep"] = df["Study_Group"] + " & " + df["Sleep_Group"]
        df["Physical_Activity_Group"] = np.where(df["Physical_Activity_Hours_Per_Day"] > median_physical,
                                                  "High Physical Activity", "Low Physical Activity")
        df["GPA_Group"] = np.where(df['GPA'] > gpa_threshold, "High GPA", "Low GPA")
        
        study_sleep_order = ['Low Study & Low Sleep', 'Low Study & High Sleep',
                            'High Study & Low Sleep', 'High Study & High Sleep']
        
        # Helper function
        def get_activity_data(df_filtered, group_name):
            if len(df_filtered) == 0:
                return None
            activity_means = df_filtered.groupby('Stress_Level')[
                ['Physical_Activity_Hours_Per_Day', 'Social_Hours_Per_Day']
            ].mean().reindex(stress_order).reset_index()
            
            df_melted = pd.melt(activity_means, id_vars=['Stress_Level'],
                               value_vars=['Physical_Activity_Hours_Per_Day', 'Social_Hours_Per_Day'],
                               var_name='Activity Type', value_name='Mean Hours')
            
            df_melted['Activity Type'] = df_melted['Activity Type'].replace({
                'Physical_Activity_Hours_Per_Day': 'Physical Activity',
                'Social_Hours_Per_Day': 'Social Hours'
            })
            df_melted['Group'] = group_name
            return df_melted
        
        # Create all data combinations
        all_data_dict = {}
        all_data_dict['All Students'] = get_activity_data(df, 'All Students')
        
        for gpa_group in ['High GPA', 'Low GPA']:
            all_data_dict[gpa_group] = get_activity_data(df[df['GPA_Group'] == gpa_group], gpa_group)
        
        for study_sleep in study_sleep_order:
            all_data_dict[study_sleep] = get_activity_data(df[df['Combined_Study_Sleep'] == study_sleep], study_sleep)
        
        for phys_group in ['High Physical Activity', 'Low Physical Activity']:
            all_data_dict[phys_group] = get_activity_data(df[df['Physical_Activity_Group'] == phys_group], phys_group)
        
        for gpa_group in ['High GPA', 'Low GPA']:
            for study_sleep in study_sleep_order:
                df_combined = df[(df['GPA_Group'] == gpa_group) & (df['Combined_Study_Sleep'] == study_sleep)]
                if len(df_combined) > 0:
                    all_data_dict[f"{gpa_group} - {study_sleep}"] = get_activity_data(df_combined, f"{gpa_group} - {study_sleep}")
        
        # Normalize sizes
        all_combined = pd.concat([v for v in all_data_dict.values() if v is not None])
        min_size, max_size = 12, 30
        all_means = all_combined['Mean Hours']
        
        def normalize_size(val):
            if all_means.max() == all_means.min():
                return (min_size + max_size) / 2
            return ((val - all_means.min()) / (all_means.max() - all_means.min())) * (max_size - min_size) + min_size
        
        for key in all_data_dict:
            if all_data_dict[key] is not None:
                all_data_dict[key]['Size'] = all_data_dict[key]['Mean Hours'].apply(normalize_size)
        
        # Create plot
        activity_colors = {'Physical Activity': '#1f77b4', 'Social Hours': '#ff7f0e'}
        stress_level_colors = {'Low': '#90EE90', 'Moderate': '#FFD700', 'High': '#FFB6C6'}
        
        title = Div(text="""
            <h2 style="color:#2c3e50; text-align:center; font-size: 24px;">Stress & GPA for Various Lifestyles</h2>
            <p style="color:#555; text-align:center; font-size: 16px;">Select different student groups to compare activity patterns</p>
        """, width=1200)
        
        p = figure(width=900, height=550, y_range=stress_order, title="All Students",
                  toolbar_location="above", tools="pan,wheel_zoom,box_zoom,reset,save")
        
        # Background bands
        for stress in stress_order:
            p.hbar(y=stress, left=0, right=all_means.max() * 1.2, height=0.8,
                  color=stress_level_colors[stress], alpha=0.15)
        
        # Initial data
        initial_data = all_data_dict['All Students']
        sources = {}
        
        for activity in ['Physical Activity', 'Social Hours']:
            subset = initial_data[initial_data['Activity Type'] == activity].copy()
            sources[activity] = ColumnDataSource(subset)
            
            p.segment(x0=0, y0='Stress_Level', x1='Mean Hours', y1='Stress_Level',
                     source=sources[activity], color='gray', alpha=0.5, line_width=2)
            
            circles = p.circle(x='Mean Hours', y='Stress_Level', size='Size',
                             source=sources[activity], color=activity_colors[activity],
                             alpha=0.8, line_color='black', line_width=1, legend_label=activity)
            
            p.add_tools(HoverTool(renderers=[circles], tooltips=[
                ("Activity", activity), ("Stress Level", "@Stress_Level"),
                ("Mean Hours", "@{Mean Hours}{0.00}"), ("Group", "@Group")
            ]))
        
        # Formatting
        p.xaxis.axis_label = "Mean Hours per Day"
        p.xaxis.axis_label_text_font_size = "16pt"
        p.xaxis.axis_label_text_font_style = "bold"
        p.xaxis.major_label_text_font_size = "14pt"
        
        p.yaxis.axis_label = "Stress Level"
        p.yaxis.axis_label_text_font_size = "16pt"
        p.yaxis.axis_label_text_font_style = "bold"
        p.yaxis.major_label_text_font_size = "15pt"
        p.yaxis.major_label_text_font_style = "bold"
        
        # Color Y-axis labels
        color_callback = CustomJS(code="""
            setTimeout(function() {
                var yTicks = document.querySelectorAll('.bk-axis.bk-left text');
                yTicks.forEach(function(tick) {
                    var text = tick.textContent.trim();
                    if (text === 'Low') tick.style.fill = '#2E7D32';
                    else if (text === 'Moderate') tick.style.fill = '#F57C00';
                    else if (text === 'High') tick.style.fill = '#C62828';
                    tick.style.fontWeight = 'bold';
                });
            }, 50);
        """)
        p.js_on_event(DocumentReady, color_callback)
        
        p.title.text_font_size = "18pt"
        p.title.text_font_style = "bold"
        p.xgrid.grid_line_dash = "dashed"
        p.xgrid.grid_line_alpha = 0.6
        p.x_range.start = 0
        p.x_range.end = all_means.max() * 1.2
        p.legend.location = "bottom_right"
        p.legend.click_policy = "hide"
        p.legend.label_text_font_size = "13pt"
        
        # Widgets
        filter_label = Div(text='<h3 style="color:#2c3e50; margin-bottom: 10px; font-size: 20px;">Filter Options:</h3>', width=280)
        
        gpa_select = Select(title="GPA Level:", value="All Students",
                           options=["All Students", "High GPA", "Low GPA"], width=280, height=50)
        
        study_sleep_select = Select(title="Study & Sleep Habits:", value="All",
                                   options=["All"] + study_sleep_order, width=280, height=50)
        
        physical_select = Select(title="Physical Activity Level:", value="All",
                                options=["All", "High Physical Activity", "Low Physical Activity"], width=280, height=50)
        
        info_box = Div(text="""
            <div style="background-color: #e7f3ff; padding: 12px; border-radius: 8px; border-left: 4px solid #1f77b4; margin-top: 20px;">
                <p style="margin: 0; color: #2c3e50; font-size: 14px;">
                    <strong>How to use:</strong><br>
                    • Select filters to view specific groups<br>
                    • Circle size = magnitude of hours<br>
                    • Hover for details
                </p>
            </div>
        """, width=280)
        
        # Convert data to JSON
        all_data_json = {k: v.to_dict('list') for k, v in all_data_dict.items() if v is not None}
        
        # Callback
        callback = CustomJS(
            args=dict(gpa_select=gpa_select, study_sleep_select=study_sleep_select, physical_select=physical_select,
                     source_phys=sources['Physical Activity'], source_social=sources['Social Hours'],
                     p=p, all_data=all_data_json),
            code="""
            const gpa = gpa_select.value;
            const study_sleep = study_sleep_select.value;
            const physical = physical_select.value;
            
            let filter_key = '';
            if (physical !== 'All') filter_key = physical;
            else if (gpa === 'All Students' && study_sleep === 'All') filter_key = 'All Students';
            else if (gpa !== 'All Students' && study_sleep === 'All') filter_key = gpa;
            else if (gpa === 'All Students' && study_sleep !== 'All') filter_key = study_sleep;
            else if (gpa !== 'All Students' && study_sleep !== 'All') filter_key = gpa + ' - ' + study_sleep;
            
            p.title.text = filter_key;
            
            if (all_data[filter_key]) {
                const new_data = all_data[filter_key];
                const phys_data = {'Stress_Level': [], 'Mean Hours': [], 'Activity Type': [], 'Group': [], 'Size': []};
                const social_data = {'Stress_Level': [], 'Mean Hours': [], 'Activity Type': [], 'Group': [], 'Size': []};
                
                for (let i = 0; i < new_data['Activity Type'].length; i++) {
                    const target = new_data['Activity Type'][i] === 'Physical Activity' ? phys_data : social_data;
                    for (let key in target) {
                        target[key].push(new_data[key][i]);
                    }
                }
                
                source_phys.data = phys_data;
                source_social.data = social_data;
            }
        """
        )
        
        gpa_select.js_on_change('value', callback)
        study_sleep_select.js_on_change('value', callback)
        physical_select.js_on_change('value', callback)
        
        controls = column(filter_label, gpa_select, study_sleep_select, physical_select, info_box, width=300)
        
        return layout([[title], [row(p, controls)]])

    # === NAVIGATION METHODS ===
    def update_slide(self):
        """Update the current slide display"""
        self.prev_button.disabled = self.current_slide == 0
        self.next_button.disabled = self.current_slide == self.total_slides - 1
        self.progress_div.text = self.get_progress_html()
        self.slide_select.value = str(self.current_slide)
        self.main_content.children = [self.slides[self.current_slide]]
        print(f"Slide {self.current_slide + 1}: {self.get_slide_title(self.current_slide)}")

    def prev_slide(self):
        if self.current_slide > 0:
            self.current_slide -= 1
            self.update_slide()

    def next_slide(self):
        if self.current_slide < self.total_slides - 1:
            self.current_slide += 1
            self.update_slide()
        elif self.auto_play:
            self.current_slide = 0
            self.update_slide()

    def go_home(self):
        self.current_slide = 0
        self.update_slide()

    def jump_to_slide(self, attr, old, new):
        self.current_slide = int(new)
        self.update_slide()

    def start_auto_play(self):
        if not self.auto_play:
            self.auto_play = True
            self.auto_play_callback = curdoc().add_periodic_callback(self.auto_advance, 5000)
            self.play_button.label = "⏸ Pause"
            self.play_button.button_type = "warning"

    def stop_auto_play(self):
        if self.auto_play:
            self.auto_play = False
            if self.auto_play_callback:
                curdoc().remove_periodic_callback(self.auto_play_callback)
            self.play_button.label = "▶ Auto Play"
            self.play_button.button_type = "success"

    def auto_advance(self):
        self.next_slide()

    def create_layout(self):
        """Create the main layout"""
        nav_bar = row(self.prev_button, self.home_button, self.next_button, self.slide_select,
                     self.play_button, self.stop_button, self.progress_div,
                     width=1000, sizing_mode="fixed", styles={"margin": "0 auto"})
        
        self.main_content = column(self.slides[0], width=1000, sizing_mode="fixed", styles={"margin": "0 auto"})
        separator = Div(text="<hr>", width=1000, styles={"margin": "6px auto"})
        
        self.layout = column(nav_bar, separator, self.main_content,
                            width=1000, sizing_mode="fixed", styles={"margin": "0 auto"})
        self.update_slide()


# === APPLICATION ENTRY POINT ===
presentation = InteractivePresentation()
curdoc().add_root(presentation.layout)
curdoc().title = "Student Lifestyle Analysis"

print("=" * 50)
print("Interactive Presentation App Started!")
print("Navigate: http://localhost:5006/presentation")
print("=" * 50)