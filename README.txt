This documentation file was generated on 04/06/2025 by Mateo Sanchez Rodriguez


GENERAL INFORMATION
-------------------

1. Title of Dataset:
Open source software for the analysis of kinematics and dynamics of machines using their linkage equations [software]

2. Authorship:

	Name: Sanchez Rodriguez, Mateo
	Institution: Universitat Politècnica de Catalunya (UPC)
	Email: mateo.sanchez@estudiantat.upc.edu
	ORCID:

	Name: Jerez Mesa, Ramón
	Institution: Universitat Politècnica de Catalunya (UPC)
	Email: ramon.jerez@upc.edu
	ORCID: 0000-0002-5084-3108

3. Contact:
	Name: Sanchez Rodriguez, Mateo
	Institution: Universitat Politècnica de Catalunya (UPC)
	Email: mateo.sanchez@estudiantat.upc.edu


DESCRIPTION
-----------

1. Dataset language:
English

2. Abstract:
This open-source computational tool is designed for the simulation and analysis of planar linkage mechanisms. Aimed at
students, educators and engineers, the software offers a flexible and intuitive environment for modeling mechanical
systems. It features a custom domain-specific language for defining mechanisms through variables, equations, and
structural data, and combines symbolic preprocessing with numerical solvers for kinematic and dynamic analysis. The
tool includes an interactive graphical user interface (GUI) for real-time configuration and visualization.
Validated through representative test cases, it delivers accurate results for position, velocity, acceleration, and
force analysis. Entirely free of proprietary dependencies, the application serves as an accessible alternative to
commercial simulation tools, promoting educational equity and supporting learning through visualization and
experimentation. (2025-05-16)

3. Keywords:
kinematics, dynamics, kinematic linkages

4. Kind of data:
Other

4. Date of data collection (single date or date range):
2024-9-12 - 2025-5-5

5. Date of dataset publication:
[Format YYYY-MM-DD]

6. Funding sources:
[Repeat the information for each funder if applicable]

	Funding agency:
	Project number:

7. Geographic location/s of data collection:
Spain


ACCESS INFORMATION
------------------

1. Creative Commons License of the dataset:
MIT License (MIT) Copyright ©

2. Dataset DOI:
[This information will be filled in by the UPCommons team after validating data.]


3. Related publication:
[Bibliographic citation of the publication related with the dataset in your discipline's standard style, including DOI.]


VERSIONING AND PROVENANCE
-------------------------

1. Last modification date:
2025-6-4


2. Was data derived from another source?:
N/A

3. Additional related data collected that was not included in the current data package:
None


METHODOLOGICAL INFORMATION
--------------------------
N/A


FILE OVERVIEW
--------------

1. Explain the file naming convention, if applicable:
N/A


2. File List:

	Directory: CDIM_app
	Sub-directories:

	Filename: Controller
	Short description: App controller files and logic helpers

	Filename: Model
	Short description: Software simulation model scripts

	Filename: UI
	Short description: App UI components and layout files

	Filename: View
	Short description: OpenGL-based rendering engine

	Filename: __main__.py
	Short description: Main executable entry point of the software


	Directory: Controller

	Filename: __init__.py
	Short description: Initializes the Controller package

	Filename: app_controller.py
	Short description: Main application controller coordinating UI and simulation

	Filename: input_compiler.py
	Short description: Parses and compiles user-defined DSL input

	Filename: run_model.py
	Short description: Handles model execution and simulation loop

	Filename: utlis.py
	Short description: Utility functions for controller-level operations

	Filename: view_controller.py
	Short description: Controls visual updates and user interaction with the View


	Directory: Model

	Filename: __init__.py
	Short description: Initializes the Model package

	Filename: link.py
	Short description: Class definitions for mechanical links and their properties

	Filename: model.py
	Short description: Core simulation logic (position, kinematics, dynamics)

	Filename: utils.py
	Short description: Helper functions for numerical methods and data processing


	Directory: UI

	Sub-directory: UI_utils

	Filename: display_buttontree.py
	Short description: Button tree for visibility and feature toggles

	Filename: NavigatonToolbar.py
	Short description: Custom navigation toolbar for interaction

	Filename: Slider_bar.py
	Short description: Time slider component for simulation control

	Filename: Test_splitter.py
	Short description: Layout testing and experimental UI management

	Filename: text_editor.py
	Short description: DSL code editor integrated into the GUI

	Filename: theme_manager.py
	Short description: Manages dark/light theme switching

	Parent directory UI:

	Filename: __init__.py
	Short description: Initializes the UI package

	Filename: mainwin_ui.py
	Short description: Main window UI logic and signals

	Filename: mainwin_ui.ui
	Short description: Qt Designer UI layout for main window

	Filename: test_ui_backup.ui
	Short description: Backup UI file for interface testing


	Directory: View

	Sub-directory: shaders (no files listed explicitly)
	Short description: Contains GLSL shaders used by the rendering engine

	Filename: __init__.py
	Short description: Initializes the View package

	Filename: opengl_view_widget.py
	Short description: Custom QOpenGLWidget for drawing simulation

	Filename: view_camera.py
	Short description: Manages camera zoom, pan, and view control


TABULAR DATA-SPECIFIC INFORMATION
---------------------------------
N/A


MORE INFORMATION
----------------
This software is stored and maintained in the following github repository: https://github.com/MateoSanRod/OpenLinkSim_app