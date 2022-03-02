
package_name=finite_difference

echo ""
echo "Re-Installing: ${package_name}"
echo ""

# uninstall using pip
python3 -m pip install --user --upgrade --no-deps --force-reinstall .

echo ""
echo "Complete"
echo ""
