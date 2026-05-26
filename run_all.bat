@echo off
cd /d C:\Users\glenn\dispatch-agent
set PYTHONIOENCODING=utf-8
echo Running news agent...
python dispatch.py --all
echo Generating site...
python generate_site.py
echo Pushing to GitHub...
git add stories.json index.html about.html resources.html trends.html community.html image_cache.json namerica.html samerica.html africa.html europe.html asia.html policing.html politics.html economics.html health.html education.html culture.html search.html highlights.json sitemap.xml robots.txt favicon.svg
git commit -m "Auto-update: fresh stories"
git push origin main
echo Done.
