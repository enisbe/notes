#/bin/bash

function env_init() {
  local env_file="environment.yaml"
  local requirements_file="requirements.txt"

  source /opt/conda/etc/profile.d/conda.sh

#   export http_proxy=http://vzproxy.keybank.com:80
#   export https_proxy=https://vzproxy.keybank.com:80
#   export HTTP_PROXY=http://vzproxy.keybank.com:80
#   export HTTP_PROXY=https://vzproxy.keybank.com:80

  echo "Setting up Python environment."


  if [ ! -f "$env_file" ]; then
    echo "Error: environment.yaml file not found."
    return 1
  fi

  if [ ! -f "$env_file" ]; then
    echo "Error: requirements.txt file not found."
    return 1
  fi


  local env_name=$(grep 'name:' $env_file | cut -d ' ' -f 2)
  if [ -z "$env_name" ]; then
    echo "Error: Environment name not found in environment.yaml."
    return 1
  fi


  if conda info --envs | grep -qw $env_name; then
    echo "Error: Environment $env_name already exists. Please choose a different name."
    return 1
  fi

  echo "Installing conda environment $env_name."

  conda env create -f $env_file
  echo "Conda environment $env_name created."

  conda activate base

#   export http_proxy=
#   export https_proxy=
#   export HTTP_PROXY=
#   export HTTP_PROXY=

  if python -c "import jupyter" &> /dev/null; then
    conda install -n $env_name ipykernel -y
    conda activate $env_name
    python -m ipykernel install --user --name $env_name --display-name "Python ($env_name)"
    echo "Jupyter Kernel $env_name successfully installed."
  else
    conda activate $env_name
    echo "Jupyter is not installed. Skipping ipykernel installation."
  fi

  if [ -f "$requirements_file" ]; then
    pip install -r $requirements_file
    echo "pip packages from $requirements_file installed."
  else
    echo "No $requirements_file found. Skipping pip install."
  fi

  echo "Python environment $env_name setup complete."
}

function remove_env() {
  local env_name=$1

  if [ -z "$env_name" ]; then
    echo "Error: No environment name provided."
    return 1
  fi


  if ! conda info --envs | grep -qw $env_name; then
    echo "Error: Environment $env_name does not exist."
    return 1
  fi

  # Deactivate current environment just in case it's active
  conda deactivate

  # Remove conda environment
  conda remove --name $env_name --all -y
  echo "Conda environment $env_name removed."

  # Remove Jupyter kernel
 
  jupyter kernelspec uninstall "$env_name" -y
  if [ $? -eq 0 ]; then
    echo "Jupyter Kernel $env_name removed."
  else
    echo "Error: Jupyter Kernel $env_name could not be removed or was not found."
  fi
}
