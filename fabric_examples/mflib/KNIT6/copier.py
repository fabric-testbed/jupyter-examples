import json
import argparse
import os
import shutil

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--slice_name", help="Name to give slice")
parser.add_argument("--notebook", help="Notebook filename to edit")
parser.add_argument("-b", "--branch", help="MF repo branch name")
parser.add_argument("-r", "--remove_last_cells", type=int, help="Remove last n cells")
#parser.add_argument("--timing", help="Add timing to cells")
parser.add_argument("-t", "--timing", action=argparse.BooleanOptionalAction, help="Add timing to cells")
parser.add_argument("--site_name", help="Site to use for slice")

KNIT6_notebooks = [
    "KNIT6_INDEX",
    "KNIT6_mflib_version_check",
    "KNIT6_prepare_a_slice_via_images",
    "KNIT6_instrumentize_a_slice",
    "KNIT6_prometheus_grafana",
    "KNIT6_elk_kibana",
    "KNIT6_mfvis_jupyternotebook_graphs",
    "KNIT6_mfvis_graph_downloading",
    "KNIT6_mf_timestamp_with_mflib",
    "KNIT6_mf_timestamp_standalone",
    "KNIT6_owl_mf", 
    "KNIT6_owl-prep_PTPDocker_slice",
    "KNIT6_owl_docker",
    "KNIT6_owl_data_analysis",
    "KNIT6_owl_data_analysis_docker"
    ]


def create_experiment_directory( dst_dir, slice_name, notebooks=KNIT6_notebooks ):

    # check if dst exists, if it does abort?
    src_dir = "."
    #dst_dir = "/home/fabric/work/KNIT6_test_copy"
    if os.path.exists(dst_dir):
        print("Directory already Exists")
        return
    os.makedirs(dst_dir)
    print(f"Created {dst_dir}")
    
    for notebook in notebooks:
        copy_notebook(src_dir, dst_dir, f"{notebook}.ipynb")
    copy_edit_notebook(src_dir, dst_dir, "KNIT6_common_imports.ipynb", slice_name)

    # copy dashboards 
    dash_src = "../dashboard_examples"
    dash_dst = os.path.join(dst_dir, "dashboard_examples")
    shutil.copytree(dash_src, dash_dst)

def copy_notebook(src_dir, dst_dir, notebook_name):
    notebook_json = load_notebook(os.path.join(src_dir, notebook_name))
    # do no editing
    save_notebook(notebook_json, os.path.join(dst_dir, notebook_name))
    
def copy_edit_notebook(src_dir, dst_dir, notebook_name, slice_name):
    notebook_json = load_notebook(os.path.join(src_dir, notebook_name))
    set_slice_name(notebook_json, slice_name)
    save_notebook(notebook_json, os.path.join(dst_dir, notebook_name))

def load_notebook(filename):
    with open(filename, "r") as f:
        notebook_json = json.load(f)
    return notebook_json

def add_timing(notebook_json):
    for cell in notebook_json["cells"]:
        if cell["cell_type"] == "code":
            if "%%time" not in cell["source"][0]:
                cell["source"].insert(0, "%%time\n")
    return notebook_json

def set_slice_name(notebook_json, slice_name):
    for cell in notebook_json["cells"]:
        if cell["cell_type"] == "code":
            for i, sourceline in enumerate(cell["source"]):
                
                if 'slice_name = "MyMonitoredSlice"' in sourceline:
                    
                    #print("Found sourceline")
                    cell["source"][i] = f'slice_name = "{slice_name}"\n' 
                    #print(sourceline)
           
                    
    return notebook_json


def set_site_name(notebook_json, site_name):
    for cell in notebook_json["cells"]:
        if cell["cell_type"] == "code":
            for i, sourceline in enumerate(cell["source"]):
                
                if 'site =' in sourceline:
                    
                    #print("Found sourceline")
                    cell["source"][i] = f'site = "{site_name}"\n' 
                    #print(sourceline)
           
                    
    return notebook_json

def set_mf_branch(notebook_json, branch):
    for cell in notebook_json["cells"]:
        if cell["cell_type"] == "code":
            for i, sourceline in enumerate(cell["source"]):         
                #if 'mflib.mf_repo_branch = ' in sourceline:
                #    cell["source"][i] = f'mflib.mf_repo_branch = "{branch}"\n' 
                
                if 'mf = MFLib(slice_name, mf_repo_branch="main")' in sourceline:
                    cell["source"][i] = f'mf = MFLib(slice_name, mf_repo_branch="{branch}")\n' 
                    
    return notebook_json

def save_notebook(notebook_json, outfilename):
    with open(outfilename, "w") as of:
        json.dump(notebook_json, of)


def remove_last_cells(notebook_json, n):
    # just remove the last 4 cells
    notebook_json["cells"] = notebook_json["cells"][:-n]
    return notebook_json

if __name__ == "__main__":
    args = parser.parse_args()
    infilename = args.notebook
    outfilename = args.notebook
    
    
    notebook_json = load_notebook(infilename)
    if args.timing:
        notebook_json = add_timing(notebook_json)
    if args.slice_name:
        notebook_json = set_slice_name(notebook_json, args.slice_name)
    if args.site_name:
        notebook_json = set_site_name(notebook_json, args.site_name)
    if args.remove_last_cells:
        notebook_json = remove_last_cells(notebook_json, args.remove_last_cells)
    if args.branch:
        notebook_json = set_mf_branch(notebook_json, args.branch)
    save_notebook(notebook_json, outfilename)