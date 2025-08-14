import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.colorbar import ColorbarBase
from matplotlib.colors import Normalize, LinearSegmentedColormap

np.random.seed(12345)

df = pd.DataFrame([np.random.normal(32000, 200000, 3650),
                   np.random.normal(43000, 100000, 3650),
                   np.random.normal(43500, 140000, 3650),
                   np.random.normal(48000, 70000, 3650)],
                  index=[1992, 1993, 1994, 1995])

means = df.mean(axis=1)
means_max = max(means)
conf_intervals = pd.Series([10000, 5000, 5000, 5000], index=[1992, 1993, 1994, 1995])
bar_colors = ['red', 'green', 'blue', 'orange']

min_y = -6000
max_y = 60000
y_value_of_interest = (min_y + max_y) / 2

y_ticks = [-6000, 0, 6500, 13000, 19500, 26000, 32500, 39000, 45500, 52000]

years = df.index
x_pos = np.arange(len(years))  # Use positions 0, 1, 2, 3 for the bars

dragging_ref_line = False

# create main figure
main_fig = plt.figure(figsize=(8, 7))
main_ax = main_fig.add_axes([0.1, 0.3, 0.8, 0.6])  # Main plot area

color_map = LinearSegmentedColormap.from_list('custom_cmap', ['darkblue', 'white', 'darkred'])
norm = Normalize(vmin=0.0, vmax=1.0)
color_ax = main_fig.add_axes([0.1, 0.1, 0.8, 0.03])
color_bar = ColorbarBase(color_ax, cmap=color_map, norm=norm, orientation='horizontal')
color_bar.set_label('Value')

bars = main_ax.bar(x_pos, means, yerr=conf_intervals, capsize=10, color=bar_colors, edgecolor='black', linewidth=1)

def create_refer_line(y_value):
    ref_line = main_ax.axhline(y=y_value, color='gray', linestyle='--', alpha=0.7, linewidth=2, picker=5)
 
    def update_reference_line(y_value):
        ref_line.set_ydata([y_value, y_value])
        y_value_text.set_text(f'{y_value:,.0f}')
        main_fig.canvas.draw_idle()

    def on_mouse_press(event):
        global dragging_ref_line
    
        if event.inaxes == main_ax:
            current_y = ref_line.get_ydata()[0]
            if abs(event.ydata - current_y) < 2000:
                dragging_ref_line = True
            ref_line.set_linestyle('-')
            ref_line.set_linewidth(3)
            ref_line.set_color('black')

    def on_mouse_motion(event):
        global dragging_ref_line
    
        if dragging_ref_line and event.inaxes == main_ax:
            update_reference_line(event.ydata)

    def on_mouse_release(event):
        global dragging_ref_line
    
        if dragging_ref_line:
            ref_line.set_linestyle('--')
            ref_line.set_linewidth(2)
            ref_line.set_color('gray')
            ref_line.set_alpha(0.7)
        
            dragging_ref_line = False

    def on_mouse_hover(event):
        if event.inaxes == main_ax and not dragging_ref_line:
            current_y = ref_line.get_ydata()[0]
            if abs(event.ydata - current_y) < 2000:
                ref_line.set_linewidth(3)
                ref_line.set_alpha(1.0)
            else:
                if not dragging_ref_line:
                    ref_line.set_linewidth(2)
                    ref_line.set_alpha(0.7)
            main_fig.canvas.draw_idle()

    main_fig.canvas.mpl_connect('button_press_event', on_mouse_press)
    main_fig.canvas.mpl_connect('motion_notify_event', on_mouse_motion)
    main_fig.canvas.mpl_connect('button_release_event', on_mouse_release)
    main_fig.canvas.mpl_connect('motion_notify_event', on_mouse_hover)

    ref_line.set_picker(True)
    return ref_line

ref_line = create_refer_line(y_value_of_interest) 

main_ax.set_xticks(x_pos)
main_ax.set_xticklabels(years)
main_ax.set_ylim(min_y, max_y)
main_ax.axhline(y=0, color='black', linewidth=0.5)

def y_fmt(y):
    if y >= 0:
        return f'{int(y):,}'
    else:
        return f'-{int(abs(y)):,}'

main_ax.yaxis.set_major_formatter(FuncFormatter(y_fmt))

y_value_text = main_ax.text(max(x_pos) + 0.5, y_value_of_interest, f'{y_value_of_interest:,.0f}', 
                      ha='left', va='center', fontsize=10, fontweight='bold',
                      bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray', boxstyle='round,pad=0.3'))

main_ax.grid(axis='y', linestyle='--', alpha=0.3)
main_ax.set_xlabel('')
main_ax.set_ylabel('')
main_ax.set_yticks(y_ticks)
main_ax.set_yticklabels(['{}', '0', '6984.5', '13023.3', '19430.0', '25680.8', '32390.5', '38738.3', '45167.1', '51595.8'])

def on_bar_click(event):
    if event.inaxes == main_ax:
        # Check if a bar was clicked
        for i, bar in enumerate(bars):
            contains, _ = bar.contains(event)
            if contains:
                year = years[i]
                value = means[year]
                conf = conf_intervals[year]
                print(color_map, color_map(value))
                for b in bars:
                    b.set_linestyle('solid')
                    b.set_facecolor(color_map(value))
                # Highlight the clicked bar
                bar.set_linestyle('dashed')
                bar.set_facecolor('white')
                main_fig.canvas.draw_idle()
                break

main_fig.canvas.mpl_connect('button_press_event', on_bar_click)

plt.tight_layout(rect=[0, 0.1, 1, 0.95])
plt.show()