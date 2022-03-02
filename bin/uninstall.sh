
package_name=finite_difference

src_dir=src
echo ""
echo "Uninstalling: ${package_name}"
echo ""

# uninstall using pip
python3 -m pip uninstall $package_name

# remove temp files/directories
rm -rf ./build
rm -rf ${src_dir}/${package_name}.egg-info

echo ""
echo "Complete"
echo ""
