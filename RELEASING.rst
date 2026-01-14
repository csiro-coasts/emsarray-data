=========
Releasing
=========

emsarray will download tutorial data files for a specific emsarray-data release.
To make a new versioned release of these tutorial data files:

1. Decide on the version tag. For this example we will publish version 1.2.3.
2. Ensure all changes are committed and pushed to the emsarray-data repository.
3. Set up the emsarray-data environment:

   .. code-block:: shell

      $ conda env create -n emsarray-data -f environment.yml
      $ conda activate emsarray-data
      $ pip install -e .

4. Generate a fresh copy of all the data files:

   .. code-block:: shell

      $ mkdir out/
      $ cd out/
      $ for x in ../scripts/download_*.py ; do python3 "$%x" ; done

5. Create and push a new tag to the repository:

   .. code-block:: shell

      $ git tag v1.2.3
      $ git push origin v1.2.3

6. Make a new release for this tag.
   Visit `<https://github.com/csiro-coasts/emsarray-data/releases/new>`_.
   Select the v1.2.3 tag you just pushed.
   Set the title to "v1.2.3".
   Press the "Generate release notes" button.
   Attach all `*.nc` files generated in the `out/` directory.
   Publish the new release.
