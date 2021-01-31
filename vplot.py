from core import *
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import warnings as w
import calibrations

# ---------- DEFINE CUSTOM PLOTTING FORMATTING ------------ #
style = "seaborn-colorblind"
plt.style.use(style)
plt.rcParams["mathtext.default"] = "regular"
plt.rcParams["mathtext.fontset"] = "dejavusans"
mpl.rcParams['patch.linewidth'] = 1
mpl.rcParams['axes.linewidth'] = 1
plt.rcParams['axes.titlesize'] = 20
plt.rcParams['axes.labelsize'] = 18
plt.rcParams['xtick.labelsize'] = 14
plt.rcParams['ytick.labelsize'] = 14
plt.rcParams['legend.fontsize'] = 14
mpl.rcParams['lines.markersize'] = 10

# Define color cycler based on plot style set here
the_rc = plt.style.library[style] #get style formatting set by plt.style.use()
color_list = the_rc['axes.prop_cycle'].by_key()['color'] * 10 #list of colors by hex code
color_cyler = the_rc['axes.prop_cycle'] #get the cycler

# ----------- MAGMASAT PLOTTING FUNCTIONS ----------- #
def smooth_isobars_and_isopleths(isobars=None, isopleths=None):
	"""
	Takes in a dataframe with calculated isobar and isopleth information (e.g., output from calculate_isobars_and_isopleths)
	and smooths the data for plotting.

	Parameters
	----------
	isobars: pandas DataFrame
		OPTIONAL. DataFrame object containing isobar information as calculated by calculate_isobars_and_isopleths.

	isopleths: pandas DataFrame
		OPTIONAL. DataFrame object containing isopleth information as calculated by calculate_isobars_and_isopleths.

	Returns
	-------
	pandas DataFrame
		DataFrame with x and y values for all isobars and all isopleths. Useful if a user wishes to do custom plotting
		with isobar and isopleth data rather than using the built-in `plot_isobars_and_isopleths()` function.
	"""
	np.seterr(divide='ignore', invalid='ignore') #turn off numpy warning
	w.filterwarnings("ignore", message="Polyfit may be poorly conditioned")

	if isobars is not None:
		P_vals = isobars.Pressure.unique()
		isobars_lists = isobars.values.tolist()
		# add zero values to volatiles list
		isobars_lists.append([0.0, 0.0, 0.0, 0.0])

		isobars_pressure = []
		isobars_H2O_liq = []
		isobars_CO2_liq = []
		# do some data smoothing
		for pressure in P_vals:
			Pxs = [item[1] for item in isobars_lists if item[0] == pressure]
			Pys = [item[2] for item in isobars_lists if item[0] == pressure]

			try:
				## calcualte polynomial
				Pz = np.polyfit(Pxs, Pys, 3)
				Pf = np.poly1d(Pz)

				## calculate new x's and y's
				Px_new = np.linspace(Pxs[0], Pxs[-1], 50)
				Py_new = Pf(Px_new)

				# Save x's and y's
				Px_new_list = list(Px_new)
				isobars_H2O_liq += Px_new_list

				Py_new_list = list(Py_new)
				isobars_CO2_liq += Py_new_list

				pressure_vals_for_list = [pressure]*len(Px_new)
				isobars_pressure += pressure_vals_for_list

			except:
				Px_list = list(Pxs)
				isobars_H2O_liq += Px_list

				Py_list = list(Pys)
				isobars_CO2_liq += Py_list

				pressure_vals_for_list = [pressure]*len(Pxs)
				isobars_pressure += pressure_vals_for_list

		isobar_df = pd.DataFrame({"Pressure": isobars_pressure,
							  "H2O_liq": isobars_H2O_liq,
							  "CO2_liq": isobars_CO2_liq})

	if isopleths is not None:
		XH2O_vals = isopleths.XH2O_fl.unique()
		isopleths_lists = isopleths.values.tolist()

		isopleths_XH2O_fl = []
		isopleths_H2O_liq = []
		isopleths_CO2_liq = []
		for Xfl in XH2O_vals:
			Xxs = [item[1] for item in isopleths_lists if item[0] == Xfl]
			Xys = [item[2] for item in isopleths_lists if item[0] == Xfl]

			try:
				## calcualte polynomial
				Xz = np.polyfit(Xxs, Xys, 2)
				Xf = np.poly1d(Xz)

				## calculate new x's and y's
				Xx_new = np.linspace(Xxs[0], Xxs[-1], 50)
				Xy_new = Xf(Xx_new)

				# Save x's and y's
				Xx_new_list = list(Xx_new)
				isopleths_H2O_liq += Xx_new_list

				Xy_new_list = list(Xy_new)
				isopleths_CO2_liq += Xy_new_list

				XH2Ofl_vals_for_list = [Xfl]*len(Xx_new)
				isopleths_XH2O_fl += XH2Ofl_vals_for_list

			except:
				Xx_list = list(Xxs)
				isopleths_H2O_liq += Xx_list

				Xy_list = list(Xys)
				isopleths_CO2_liq += Xy_list

				XH2Ofl_vals_for_list = [Xfl]*len(Xxs)
				isopleths_XH2O_fl += XH2Ofl_vals_for_list

		isopleth_df = pd.DataFrame({"XH2O_fl": isopleths_XH2O_fl,
							  "H2O_liq": isopleths_H2O_liq,
							  "CO2_liq": isopleths_CO2_liq})

	np.seterr(divide='warn', invalid='warn') #turn numpy warning back on
	w.filterwarnings("always", message="Polyfit may be poorly conditioned")

	if isobars is not None:
		if isopleths is not None:
			return isobar_df, isopleth_df
		else:
			return isobar_df
	else:
		if isopleths is not None:
			return isopleth_df


def plot(isobars=None, isopleths=None, degassing_paths=None, custom_H2O=None, custom_CO2=None,
		 isobar_labels=None, isopleth_labels=None, degassing_path_labels=None, custom_labels=None,
		 custom_colors="VESIcal", custom_symbols=None, markersize=10, figsize=(12,8), save_fig=False,
		 extend_isobars_to_zero=True, smooth_isobars=False, smooth_isopleths=False, **kwargs):
	"""
	Custom automatic plotting of model calculations in VESIcal.
	Isobars, isopleths, and degassing paths can be plotted. Labels can be specified for each.
	Any combination of isobars, isopleths, and degassing paths can be plotted.

	Parameters
	----------
	isobars: pandas DataFrame or list
		OPTIONAL. DataFrame object containing isobar information as calculated by calculate_isobars_and_isopleths. Or a list
		of DataFrame objects.

	isopleths: pandas DataFrame or list
		OPTIONAL. DataFrame object containing isopleth information as calculated by calculate_isobars_and_isopleths. Or a list
		of DataFrame objects.

	degassing_paths: list
		OPTIONAL. List of DataFrames with degassing information as generated by calculate_degassing_path().

	custom_H2O: list
		OPTIONAL. List of groups of H2O values to plot as points. For example myfile.data['H2O'] is one group of H2O values.
		Must be passed with custom_CO2 and must be same length as custom_CO2.

	custom_CO2: list
		OPTIONAL. List of groups of CO2 values to plot as points.For example myfile.data['CO2'] is one group of CO2 values.
		Must be passed with custom_H2O and must be same length as custom_H2O.

	isobar_labels: list
		OPTIONAL. Labels for the plot legend. Default is None, in which case each plotted line will be given the generic
		legend name of "Isobars n", with n referring to the nth isobars passed. Isobar pressure is given in parentheses.
		The user can pass their own labels as a list of strings. If more than one set of isobars is passed, the labels should
		refer to each set of isobars, not each pressure.

	isopleth_labels: list
		OPTIONAL. Labels for the plot legend. Default is None, in which case each plotted isopleth will be given the generic
		legend name of "Isopleth n", with n referring to the nth isopleths passed. Isopleth XH2O values are given in
		parentheses. The user can pass their own labels as a list of strings. If more than one set of isopleths is passed,
		the labels should refer to each set of isopleths, not each XH2O value.

	degassing_path_labels: list
		OPTIONAL. Labels for the plot legend. Default is None, in which case each plotted line will be given the generic
		legend name of "Pathn", with n referring to the nth degassing path passed. The user can pass their own labels
		as a list of strings.

	custom_labels: list
		OPTIONAL. Labels for the plot legend. Default is None, in which case each group of custom points will be given the
		generic legend name of "Customn", with n referring to the nth degassing path passed. The user can pass their own labels
		as a list of strings.

	custom_colors: list
		OPTIONAL. Default value is "VESIcal", which uses VESIcal's color ramp. A list of color values readable by matplotlib
		can be passed here if custom symbol colors are desired. The length of this list must match that of custom_H2O and
		custom_CO2.

	custom_symbols: list
		OPTIONAL. Default value is None, in which case data are plotted as filled circles.. A list of symbol tyles readable
		by matplotlib can be passed here if custom symbol types are desired. The length of this list must match that of
		custom_H2O and custom_CO2.

	markersize: int
		OPTIONAL. Default value is 10. Same as markersize kwarg in matplotlib. Any numeric value passed here will set the
		marker size for (custom_H2O, custom_CO2) points.

	figsize: tuple
		OPTIONAL. Default value is (12,8). Sets the matplotlib.pyplot figsize value as (x_dimension, y_dimension)

	save_fig: False or str
		OPTIONAL. Default value is False, in which case the figure will not be saved. If a string is passed,
		the figure will be saved with the string as the filename. The string must include the file extension.

	extend_isobars_to_zero: bool
		OPTIONAL. If True (default), isobars will be extended to zero, even if there is a finite solubility at zero partial pressure.

	smooth_isobars: bool
		OPTIONAL. Default is False. If set to True, isobar data will be fit to a polynomial and plotted. If False, the raw input data
		will be plotted.

	smooth_isopleths: bool
		OPTIONAL. Default is False. If set to True, isopleth data will be fit to a polynomial and plotted. If False, the raw input data
		will be plotted.

	Returns
	-------
	matplotlib object
		Plot with x-axis as H2O wt% in the melt and y-axis as CO2 wt% in the melt. Isobars, or lines of
		constant pressure at which the sample magma composition is saturated, and isopleths, or lines of constant
		fluid composition at which the sample magma composition is saturated, are plotted if passed. Degassing
		paths, or the concentration of dissolved H2O and CO2 in a melt equilibrated along a path of decreasing
		pressure, is plotted if passed.
	"""
	np.seterr(divide='ignore', invalid='ignore') #turn off numpy warning
	w.filterwarnings("ignore", message="Polyfit may be poorly conditioned")

	if custom_H2O is not None:
		if custom_CO2 is None:
			raise InputError("If x data is passed, y data must also be passed.")
		else:
			if len(custom_H2O) == len(custom_CO2):
				pass
			else:
				raise InputError("x and y data must be same length")
	if custom_CO2 is not None:
		if custom_H2O is None:
			raise InputError("If y data is passed, x data must also be passed.")

	if custom_colors == "VESIcal":
		use_colors = color_list
	elif isinstance(custom_colors, list):
		use_colors = custom_colors
	else:
		raise InputError("Argument custom_colors must be type list. Just passing one item? Try putting square brackets, [], around it.")

	plt.figure(figsize=figsize)
	if 'custom_x' in kwargs:
		plt.xlabel(kwargs['xlabel'])
		plt.ylabel(kwargs['ylabel'])
	else:
		plt.xlabel('H$_2$O wt%')
		plt.ylabel('CO$_2$ wt%')

	labels = []

	if isobars is not None:
		if isinstance(isobars, pd.DataFrame):
			isobars = [isobars]

		for i in range(len(isobars)):
			P_vals = isobars[i].Pressure.unique()
			isobars_lists = isobars[i].values.tolist()

			# add zero values to volatiles list
			isobars_lists.append([0.0, 0.0, 0.0, 0.0])

			P_iter = 0
			for pressure in P_vals:
				P_iter += 1
				Pxs = [item[1] for item in isobars_lists if item[0] == pressure]
				Pys = [item[2] for item in isobars_lists if item[0] == pressure]

				if len(isobars) > 1:
					if P_iter == 1:
						P_list = [int(i) for i in P_vals]
						if isinstance(isobar_labels, list):
							labels.append(str(isobar_labels[i]) + ' (' + ', '.join(map(str, P_list)) + " bars)")
						else:
							labels.append('Isobars ' + str(i+1) + ' (' + ', '.join(map(str, P_list)) + " bars)")
					else:
						labels.append('_nolegend_')
				if smooth_isobars == True:
				# do some data smoothing
					try:
						## calcualte polynomial
						Pz = np.polyfit(Pxs, Pys, 3)
						Pf = np.poly1d(Pz)

						## calculate new x's and y's
						Px_new = np.linspace(Pxs[0], Pxs[-1], 50)
						Py_new = Pf(Px_new)

						if extend_isobars_to_zero == True and Px_new[0]*Py_new[0] != 0.0:
							if Px_new[0] > Py_new[0]:
								Px_newer = np.zeros(np.shape(Px_new)[0]+1)
								Px_newer[0] = 0
								Px_newer[1:] = Px_new
								Px_new = Px_newer

								Py_newer = np.zeros(np.shape(Py_new)[0]+1)
								Py_newer[0] = Py_new[0]
								Py_newer[1:] = Py_new
								Py_new = Py_newer
							else:
								Px_newer = np.zeros(np.shape(Px_new)[0]+1)
								Px_newer[0] = Px_new[0]
								Px_newer[1:] = Px_new
								Px_new = Px_newer

								Py_newer = np.zeros(np.shape(Py_new)[0]+1)
								Py_newer[0] = 0
								Py_newer[1:] = Py_new
								Py_new = Py_newer

						if extend_isobars_to_zero == True and Px_new[-1]*Py_new[-1] != 0.0:
							if Px_new[-1] < Py_new[-1]:
								Px_newer = np.zeros(np.shape(Px_new)[0]+1)
								Px_newer[-1] = 0
								Px_newer[:-1] = Px_new
								Px_new = Px_newer

								Py_newer = np.zeros(np.shape(Py_new)[0]+1)
								Py_newer[-1] = Py_new[-1]
								Py_newer[:-1] = Py_new
								Py_new = Py_newer
							else:
								Px_newer = np.zeros(np.shape(Px_new)[0]+1)
								Px_newer[-1] = Px_new[-1]
								Px_newer[:-1] = Px_new
								Px_new = Px_newer

								Py_newer = np.zeros(np.shape(Py_new)[0]+1)
								Py_newer[-1] = 0
								Py_newer[:-1] = Py_new
								Py_new = Py_newer

						# Plot some stuff
						if len(isobars) > 1:
							plt.plot(Px_new, Py_new, color=color_list[i])
						else:
							plt.plot(Px_new, Py_new)
					except:
						if len(isobars) > 1:
							plt.plot(Pxs, Pys, color=color_list[i])
						else:
							plt.plot(Pxs, Pys)

				elif smooth_isobars == False:
					if extend_isobars_to_zero == True and Pxs[0]*Pys[0] != 0.0:
						if Pxs[0] > Pys[0]:
							Px_newer = np.zeros(np.shape(Pxs)[0]+1)
							Px_newer[0] = 0
							Px_newer[1:] = Pxs
							Pxs = Px_newer

							Py_newer = np.zeros(np.shape(Pys)[0]+1)
							Py_newer[0] = Pys[0]
							Py_newer[1:] = Pys
							Pys = Py_newer
						else:
							Px_newer = np.zeros(np.shape(Pxs)[0]+1)
							Px_newer[0] = Pxs[0]
							Px_newer[1:] = Pxs
							Pxs = Px_newer

							Py_newer = np.zeros(np.shape(Pys)[0]+1)
							Py_newer[0] = 0
							Py_newer[1:] = Pys
							Pys = Py_newer

					if extend_isobars_to_zero == True and Pxs[-1]*Pys[-1] != 0.0:
						if Pxs[-1] < Pys[-1]:
							Px_newer = np.zeros(np.shape(Pxs)[0]+1)
							Px_newer[-1] = 0
							Px_newer[:-1] = Pxs
							Pxs = Px_newer

							Py_newer = np.zeros(np.shape(Pys)[0]+1)
							Py_newer[-1] = Pys[-1]
							Py_newer[:-1] = Pys
							Pys = Py_newer
						else:
							Px_newer = np.zeros(np.shape(Pxs)[0]+1)
							Px_newer[-1] = Pxs[-1]
							Px_newer[:-1] = Pxs
							Pxs = Px_newer

							Py_newer = np.zeros(np.shape(Pys)[0]+1)
							Py_newer[-1] = 0
							Py_newer[:-1] = Pys
							Pys = Py_newer
					if len(isobars) > 1:
						plt.plot(Pxs, Pys, color=color_list[i])
					else:
						plt.plot(Pxs, Pys)

			if len(isobars) == 1:
				labels = [str(P_val) + " bars" for P_val in P_vals]

	if isopleths is not None:
		if isinstance(isopleths, pd.DataFrame):
			isopleths = [isopleths]

		for i in range(len(isopleths)):
			XH2O_vals = isopleths[i].XH2O_fl.unique()
			isopleths_lists = isopleths[i].values.tolist()

			H_iter = 0
			for Xfl in XH2O_vals:
				H_iter += 1
				Xxs = [item[1] for item in isopleths_lists if item[0] == Xfl]
				Xys = [item[2] for item in isopleths_lists if item[0] == Xfl]

				if len(isopleths) > 1:
					if H_iter == 1:
						H_list = [i for i in XH2O_vals]
						if isinstance(isopleth_labels, list):
							labels.append(str(isopleth_labels[i]) + ' (' + ', '.join(map(str, H_list)) + " XH2Ofluid)")
						else:
							labels.append('Isopleths ' + str(i+1) + ' (' + ', '.join(map(str, H_list)) + " XH2Ofluid)")
					else:
						labels.append('_nolegend_')
				if smooth_isopleths == True:
				# do some data smoothing
					try:
						## calcualte polynomial
						Xz = np.polyfit(Xxs, Xys, 2)
						Xf = np.poly1d(Xz)

						## calculate new x's and y's
						Xx_new = np.linspace(Xxs[0], Xxs[-1], 50)
						Xy_new = Xf(Xx_new)

						# Plot some stuff
						if len(isopleths) == 1:
							plt.plot(Xx_new, Xy_new, ls='dashed', color='k')
						else:
							plt.plot(Xx_new, Xy_new, ls='dashed', color=color_list[i])
					except:
						if len(isopleths) == 1:
							plt.plot(Xxs, Xys, ls='dashed', color='k')
						else:
							plt.plot(Xxs, Xys, ls='dashed', color=color_list[i])

				elif smooth_isopleths == False:
					if len(isopleths) == 1:
							plt.plot(Xxs, Xys, ls='dashed', color='k')
					else:
						plt.plot(Xxs, Xys, ls='dashed', color=color_list[i])

			if len(isopleths) == 1:
				H_list = [i for i in XH2O_vals]
				iso_label_iter = 0
				for i in XH2O_vals:
					iso_label_iter += 1
					if iso_label_iter == 1:
						labels.append('Isopleths (' + ', '.join(map(str, H_list)) + " XH2Ofluid)")
					else:
						labels.append('_nolegend_')

	if degassing_paths is not None:
		if isinstance(degassing_paths, pd.DataFrame):
			degassing_paths = [degassing_paths]

		degassing_colors = color_list.copy()
		#degassing_colors.reverse()
		iterno = 0
		for i in range(len(degassing_paths)):
			if degassing_path_labels == None:
				iterno += 1
				labels.append('Path%s' %iterno)
				plt.plot(degassing_paths[i]["H2O_liq"], degassing_paths[i]["CO2_liq"], ls='dotted', color=degassing_colors[i])
			else:
				labels.append(degassing_path_labels[iterno])
				plt.plot(degassing_paths[i]["H2O_liq"], degassing_paths[i]["CO2_liq"], ls='dotted', color=degassing_colors[i])
				iterno += 1

		for i in range(len(degassing_paths)):
			plt.plot(degassing_paths[i]["H2O_liq"].max(), degassing_paths[i]["CO2_liq"].max(), 'o', color=degassing_colors[i])
			labels.append('_nolegend_')

	if custom_H2O is not None and custom_CO2 is not None:
		if isinstance(custom_H2O, pd.DataFrame):
			custom_H2O = [custom_H2O]
		if isinstance(custom_CO2, pd.DataFrame):
			custom_CO2 = [custom_CO2]

		if custom_symbols == None:
			use_marker = ['o'] * len(custom_H2O)
		else:
			use_marker = custom_symbols

		iterno = 0
		for i in range(len(custom_H2O)):
			if custom_labels == None:
				iterno +=1
				labels.append('Custom%s' %iterno)
				plt.plot(custom_H2O[i], custom_CO2[i], use_marker[i], color=use_colors[i], markersize=markersize)
			else:
				labels.append(custom_labels[iterno])
				plt.plot(custom_H2O[i], custom_CO2[i], use_marker[i], color=use_colors[i], markersize=markersize)
				iterno += 1

	if 'custom_x' in kwargs:
			custom_x = kwargs['custom_x']
			custom_y = kwargs['custom_y']
			xlabel = kwargs['xlabel']
			ylabel = kwargs['ylabel']

			if isinstance(custom_x, pd.core.series.Series):
				custom_x = [list(custom_x.values)]
			if isinstance(custom_y, pd.core.series.Series):
				custom_y = [list(custom_y.values)]

			if custom_symbols == None:
				use_marker = ['o'] * len(custom_x)
			else:
				use_marker = custom_symbols

			iterno = 0
			for i in range(len(custom_x)):
				if custom_labels == None:
					iterno +=1
					labels.append('Custom%s' %iterno)
					plt.plot(custom_x[i], custom_y[i], use_marker[i], color=use_colors[i], markersize=markersize)
				else:
					labels.append(custom_labels[iterno])
					plt.plot(custom_x[i], custom_y[i], use_marker[i], color=use_colors[i], markersize=markersize)
					iterno += 1


	plt.legend(labels, bbox_to_anchor=(1.01,1), loc='upper left')

	if 'custom_x' not in kwargs:
		plt.xlim(left=0)
		plt.ylim(bottom=0)

	np.seterr(divide='warn', invalid='warn') #turn numpy warning back on
	w.filterwarnings("always", message="Polyfit may be poorly conditioned")

	if isinstance(save_fig, str):
		plt.savefig(save_fig)

	return plt.show()

def scatterplot(custom_x, custom_y, xlabel=None, ylabel=None, **kwargs):
	"""
	Custom x-y plotting using VESIcal's built-in plot() function, built on Matplotlib's plot and scatter functions.

	Parameters
	----------
	custom_x: list
		List of groups of x-values to plot as points or lines

	custom_y: list
		List of groups of y-values to plot as points or lines

	xlabel: str
		OPTIONAL. What to display along the x-axis.

	ylabel: str
		OPTIONAL. What to display along the y-axis.

	kwargs:
		Can take in any key word agruments that can be passed to `plot()`.

	Returns
	-------
	matplotlib object
		X-y plot with custom x and y axis values and labels.
	"""

	if isinstance(custom_x, list) and isinstance(custom_y, list):
		if len(custom_x) != len(custom_y):
			raise InputError("X and y lists must be same length")

	if xlabel is not None:
		if isinstance(xlabel, str):
			pass
		else:
			raise InputError("xlabel must be string")

	if ylabel is not None:
		if isinstance(ylabel, str):
			pass
		else:
			raise InputError("ylabel must be string")

	return plot(custom_x=custom_x, custom_y=custom_y, xlabel=xlabel, ylabel=ylabel, **kwargs)

# ------- Define custom plotting tools for checking calibrations ------- #
# -------------------------------------------------------- #
#    			   TAS PLOT PYTHON SCRIPT          	       #
#														   #
#  COPYRIGHT:  (C) 2015 John A Stevenson / @volcan01010    #
#                       Joaquin Cortés					   #
#  WEBSITE: http://all-geo.org/volcan01010				   #
# -------------------------------------------------------- #
def add_LeMaitre_fields(plot_axes, fontsize=12, color=(0.6, 0.6, 0.6)):
	"""Add fields for geochemical classifications from LeMaitre et al (2002)
	to pre-existing axes.  If necessary, the axes object can be retrieved via
	plt.gca() command. e.g.

	ax1 = plt.gca()
	add_LeMaitre_fields(ax1)
	ax1.plot(silica, total_alkalis, 'o')

	Fontsize and color options can be used to change from the defaults.

	It may be necessary to follow the command with plt.draw() to update
	the plot.

	Le Maitre RW (2002) Igneous rocks : IUGS classification and glossary of
		terms : recommendations of the International Union of Geological
		Sciences Subcommission on the Systematics of igneous rocks, 2nd ed.
		Cambridge University Press, Cambridge
	"""
	from collections import namedtuple
	# Prepare the field information
	FieldLine = namedtuple('FieldLine', 'x1 y1 x2 y2')
	lines = (FieldLine(x1=41, y1=0, x2=41, y2=7),
			 FieldLine(x1=41, y1=7, x2=52.5, y2=14),
			 FieldLine(x1=45, y1=0, x2=45, y2=5),
			 FieldLine(x1=41, y1=3, x2=45, y2=3),
			 FieldLine(x1=45, y1=5, x2=61, y2=13.5),
			 FieldLine(x1=45, y1=5, x2=52, y2=5),
			 FieldLine(x1=52, y1=5, x2=69, y2=8),
			 FieldLine(x1=49.4, y1=7.3, x2=52, y2=5),
			 FieldLine(x1=52, y1=5, x2=52, y2=0),
			 FieldLine(x1=48.4, y1=11.5, x2=53, y2=9.3),
			 FieldLine(x1=53, y1=9.3, x2=57, y2=5.9),
			 FieldLine(x1=57, y1=5.9, x2=57, y2=0),
			 FieldLine(x1=52.5, y1=14, x2=57.6, y2=11.7),
			 FieldLine(x1=57.6, y1=11.7, x2=63, y2=7),
			 FieldLine(x1=63, y1=7, x2=63, y2=0),
			 FieldLine(x1=69, y1=12, x2=69, y2=8),
			 FieldLine(x1=45, y1=9.4, x2=49.4, y2=7.3),
			 FieldLine(x1=69, y1=8, x2=77, y2=0))

	FieldName = namedtuple('FieldName', 'name x y rotation')
	names = (FieldName('Picro\nbasalt', 43, 2, 0),
			 FieldName('Basalt', 48.5, 2, 0),
			 FieldName('Basaltic\nandesite', 54.5, 2, 0),
			 FieldName('Andesite', 60, 2, 0),
			 FieldName('Dacite', 68.5, 2, 0),
			 FieldName('Rhyolite', 76, 9, 0),
			 FieldName('Trachyte\n(Q < 20%)\n\nTrachydacite\n(Q > 20%)',
					   64.5, 11.5, 0),
			 FieldName('Basaltic\ntrachyandesite', 53, 8, -20),
			 FieldName('Trachy-\nbasalt', 49, 6.2, 0),
			 FieldName('Trachyandesite', 57.2, 9, 0),
			 FieldName('Phonotephrite', 49, 9.6, 0),
			 FieldName('Tephriphonolite', 53.0, 11.8, 0),
			 FieldName('Phonolite', 57.5, 13.5, 0),
			 FieldName('Tephrite\n(Ol < 10%)', 45, 8, 0),
			 FieldName('Foidite', 44, 11.5, 0),
			 FieldName('Basanite\n(Ol > 10%)', 43.5, 6.5, 0))

	# Plot the lines and fields
	for line in lines:
		plot_axes.plot([line.x1, line.x2], [line.y1, line.y2],
					   '-', color=color, zorder=0)
	for name in names:
		plot_axes.text(name.x, name.y, name.name, color=color, size=fontsize,
				 horizontalalignment='center', verticalalignment='top',
				 rotation=name.rotation, zorder=0)

def calib_plot(user_data=None, model='all', plot_type='TAS', zoom=None, figsize=(17,8), legend=True, save_fig=False, **kwargs):
	"""
	Plots user data and calibration set of any or all models on any x-y plot or a total alkalis vs silica (TAS) diagram.
	TAS diagram boundaries provided by tasplot python module, copyright John A Stevenson.

	Parameters
	----------
	user_data: BatchFile object, pandas DataFrame, pandas Series, or dict
		OPTIONAL. Default value is None, in which case only the model calibration set is plotted.
		User provided sample data describing the oxide composition of one or more samples. Multiple samples
		can be passed as an BatchFile object or pandas DataFrame. A single sample can be passed as a pandas
		Series.

	model: str or list
		OPTIONAL. Default value is 'all', in which case all model calibration datasets will be plotted.
		'Mixed' can be used to plot all mixed fluid models.
		String of the name of the model calibration dataset to plot (e.g., 'Shishkina'). Multiple models
		can be plotted by passing them as strings within a list (e.g., ['Shishkina', 'Dixon']).

	plot_type: str
		OPTIONAL. Default value is 'TAS', which returns a total alkali vs silica (TAS) diagram. Any two oxides can
		be plotted as an x-y plot by setting plot_type='xy' and specifying x- and y-axis oxides, e.g., x='SiO2', y='Al2O3'

	zoom: str or list
		OPTIONAL. Default value is None in which case axes will be set to the default of 35<x<100 wt% and 0<y<25 wt% for
		TAS type plots and the best values to show the data for xy type plots. Can pass "user_data" to plot the figure
		where the x and y axes are scaled down to zoom in and only show the region surrounding the user_data. A list of
		tuples may be passed to manually specify x and y limits. Pass in data as  [(x_min, x_max), (y_min, y_max)].
		For example, the default limits here would be passed in as [(35,100), (0,25)].

	figsize: tuple
		OPTIONAL. Default value is (17,8). Sets the matplotlib.pyplot figsize value as (x_dimension, y_dimension)

	legend: bool
		OPTIONAL. Default value is True. Can be set to False in which case the legend will not be displayed.

	save_fig: False or str
		OPTIONAL. Default value is False, in which case the figure will not be saved. If a string is passed,
		the figure will be saved with the string as the filename. The string must include the file extension.

	Returns
	-------
	matplotlib object
	"""

	#Get x and y axis limits, if user passed them
	if zoom == None:
		user_xmin = 35
		user_xmax = 100
		user_ymin = 0
		user_ymax = 25
	elif zoom == 'user_data':
		if isinstance(user_data, BatchFile) or isinstance(user_data, pd.DataFrame):
			print("'user_data' type zoom for more than one sample is not implemented yet.")
			user_xmin = 35
			user_xmax = 100
			user_ymin = 0
			user_ymax = 25
		elif isinstance(user_data, pd.core.series.Series) or isinstance(user_data, dict):
			user_xmin = user_data['SiO2'] - 5
			user_xmax = user_data['SiO2'] + 5
			user_ymin = user_data['Na2O'] + user_data['K2O'] - 2
			if user_ymin <0:
				user_ymin = 0
			user_ymax = user_data['Na2O'] + user_data['K2O'] + 2
	elif isinstance(zoom, list):
		user_xmin, user_xmax = zoom[0]
		user_ymin, user_ymax = zoom[1]

	#Create the figure
	fig, ax1 = plt.subplots(figsize = figsize)
	font = {'family': 'sans-serif',
				'color':  'black',
				'weight': 'normal',
				'size': 20,
				}

	#TAS figure
	if plot_type == 'TAS':
		ax1.set_xlim([user_xmin, user_xmax]) # adjust x limits here if you want to focus on a specific part of compostional space
		ax1.set_ylim([user_ymin, user_ymax]) # adjust y limits here
		plt.xlabel('SiO$_2$, wt%', fontdict=font, labelpad = 15)
		plt.ylabel('Na$_2$O+K$_2$O, wt%', fontdict=font, labelpad = 15)
		if zoom == None:
			add_LeMaitre_fields(ax1)
	elif plot_type == 'xy':
		if 'x' in kwargs and 'y' in kwargs:
			x = kwargs['x']
			y = kwargs['y']
			if zoom != None:
				ax1.set_xlim([user_xmin, user_xmax])
				ax1.set_ylim([user_ymin, user_ymax])
			plt.xlabel(str(x)+", wt%", fontdict=font, labelpad = 15)
			plt.ylabel(str(y)+", wt%", fontdict=font, labelpad = 15)
		else:
			raise InputError("If plot_type is 'xy', then x and y values must be passed as strings. For example, x='SiO2', y='Al2O3'.")

	#Plot Calibration Data
	if model == 'all':
		model = ['MagmaSat',
				'Shishkina',
				'Dixon',
				'IaconoMarziano',
				'Liu',
				#'EguchiCarbon',
				'AllisonCarbon',
				'MooreWater']
	if model == 'mixed':
		model = ['MagmaSat',
				 'Shishkina',
				 'Dixon',
				 'IaconoMarziano',
				 'Liu']

	if isinstance(model, str):
		model = [model]

	if isinstance(model, list):
		for modelname in model:
			model_type = calibrations.return_calibration_type(modelname)
			if model_type['H2O'] == True:
				h2o_legend = True
			if model_type['CO2'] == True or model_type['Mixed'] == True:
				co2_h2oco2_legend = True

		if h2o_legend == True:
			plt.scatter([], [], marker='', label=r"$\bf{Pure \ H_2O:}$")

			for modelname in model:
				calibdata = calibrations.return_calibration(modelname)
				model_type = calibrations.return_calibration_type(modelname)
				if isinstance(calibdata, str):
					w.warn(calibdata)
				else:
					if model_type['H2O'] == True:
						if plot_type == 'TAS':
							try:
								plt.scatter(calibdata['H2O']['SiO2'], calibdata['H2O']['Na2O'] + calibdata['H2O']['K2O'],
											marker='s', facecolors=calibdata['facecolor'], edgecolors='k', label=str(modelname))
							except:
								plt.scatter(calibdata['H2O']['SiO2'], calibdata['H2O']['Na2O+K2O'],
											marker='s', facecolors=calibdata['facecolor'], edgecolors='k', label=str(modelname))
						if plot_type == 'xy':
							try:
								plt.scatter(calibdata['H2O'][x], calibdata['H2O'][y],
											marker='s', facecolors=calibdata['facecolor'], edgecolors='k', label=str(modelname))
							except:
								w.warn("The requested oxides were not found in the calibration dataset for " + str(modelname) + ".")

			if co2_h2oco2_legend == True:
				plt.scatter([], [], marker='', label=r"${\ }$")

		if co2_h2oco2_legend == True:
			plt.scatter([], [], marker='', label=r"$\bf{\ CO_2 \ and \ H_2O\!-\!CO_2:}$")

		for modelname in model:
			calibdata = calibrations.return_calibration(modelname)
			model_type = calibrations.return_calibration_type(modelname)
			if isinstance(calibdata, str):
				w.warn(calibdata)
			else:
				if model_type['CO2'] == True and model_type['Mixed'] == True:
					frames = [calibdata['CO2'], calibdata['Mixed']]
					co2_and_mixed = pd.concat(frames)
					if plot_type == 'TAS':
						try:
							plt.scatter(co2_and_mixed['SiO2'], co2_and_mixed['Na2O'] + co2_and_mixed['K2O'],
										marker='d', facecolors=calibdata['facecolor'], edgecolors='k', label=str(modelname))
						except:
							plt.scatter(co2_and_mixed['SiO2'], co2_and_mixed['Na2O+K2O'],
									marker='d', facecolors=calibdata['facecolor'], edgecolors='k', label=str(modelname))
					if plot_type == 'xy':
						try:
							plt.scatter(co2_and_mixed[x], co2_and_mixed[y],
									marker='d', facecolors=calibdata['facecolor'], edgecolors='k', label=str(modelname))
						except:
							w.warn("The requested oxides were not found in the calibration dataset for " + str(modelname) + ".")
				elif model_type['CO2'] == True or model_type['Mixed'] == True:
					if model_type['CO2'] == True:
						thistype = 'CO2'
					if model_type['Mixed'] == True:
						thistype = 'Mixed'
					if plot_type == 'TAS':
						try:
							plt.scatter(calibdata[thistype]['SiO2'], calibdata[thistype]['Na2O'] + calibdata[thistype]['K2O'],
										marker='d', facecolors=calibdata['facecolor'], edgecolors='k', label=str(modelname))
						except:
							plt.scatter(calibdata[thistype]['SiO2'], calibdata[thistype]['Na2O+K2O'],
									marker='d', facecolors=calibdata['facecolor'], edgecolors='k', label=str(modelname))
					if plot_type == 'xy':
						try:
							plt.scatter(calibdata[thistype][x], calibdata[thistype][y],
									marker='d', facecolors=calibdata['facecolor'], edgecolors='k', label=str(modelname))
						except:
							w.warn("The requested oxides were not found in the calibration dataset for " + str(modelname) + ".")
	else:
		raise InputError("model must be of type str or list")

	#Plot user data
	if user_data is None:
		pass
	else:
		if isinstance(user_data, BatchFile):
			user_data = user_data.data
		if plot_type == 'TAS':
			_sample = user_data.copy()
			try:
				_sample["TotalAlkalis"] = _sample["Na2O"] + _sample["K2O"]
			except:
				InputError("Na2O and K2O data must be in user_data")
			plt.scatter(_sample['SiO2'], _sample['TotalAlkalis'],
						s=150, edgecolors='w', facecolors='red', marker='P',
						label = 'User Data')
		if plot_type == 'xy':
			_sample = user_data.copy()
			plt.scatter(_sample[x], _sample[y],
						s=150, edgecolors='w', facecolors='red', marker='P',
						label = 'User Data')

	if legend == True:
		plt.legend(bbox_to_anchor=(1.04,1), loc="upper left")
	fig.tight_layout()
	if isinstance(save_fig, str):
		fig.savefig(save_fig)

	return plt.show()