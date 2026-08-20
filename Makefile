# Makefile para automatizar los comandos de Docker del proyecto

.PHONY: help up down logs restart clean psql jupyter

# Comando por defecto
help:
	@echo "Comandos disponibles:"
	@echo "  make up      - Levanta los contenedores en segundo plano (detached)"
	@echo "  make down    - Detiene y remueve los contenedores"
	@echo "  make logs    - Muestra los logs de todos los contenedores en tiempo real"
	@echo "  make restart - Reinicia los contenedores"
	@echo "  make clean   - Detiene los contenedores y elimina los volúmenes (BORRA LA BD)"
	@echo "  make psql    - Abre una consola interactiva de PostgreSQL"
	@echo "  make jupyter - Muestra el enlace y token para acceder a JupyterLab"

# Levantar infraestructura
up:
	docker-compose up -d

# Bajar infraestructura
down:
	docker-compose down

# Ver logs
logs:
	docker-compose logs -f

# Reiniciar servicios
restart:
	docker-compose restart

# Limpieza total (elimina base de datos)
clean:
	docker-compose down -v
	@echo "¡Volúmenes y contenedores eliminados!"

# Consola PostgreSQL
psql:
	docker exec -it db_movilidad psql -U postgres -d movilidad

# Info JupyterLab
jupyter:
	@echo "Accede a JupyterLab en tu navegador: http://localhost:8888"
	@echo "El token de acceso es: analitica2026"
