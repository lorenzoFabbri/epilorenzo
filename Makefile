.PHONY: clean render preview help

help:
	@echo "Available commands:"
	@echo "  make clean    - Remove rendered output and temporary files"
	@echo "  make render   - Render the website"
	@echo "  make preview  - Preview the website locally"

clean:
	@echo "Cleaning rendered output and temporary files..."
	rm -rf docs/
	rm -rf .quarto/
	@echo "Done!"

render:
	quarto render

preview:
	quarto preview
