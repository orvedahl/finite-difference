
package_name=finite_difference

echo ""
echo "Installing: ${package_name}"
echo ""

# uninstall using pip
python3 -m pip -vv install --user .

if [ $? -eq 0 ]; then
    echo ""
    echo "Complete"
    echo ""
fi
