docker run --name my-mysql   -e MYSQL_ROOT_PASSWORD=seqato123 -e MYSQL_DATABASE=stocks_db -p 3306:3306   -d mysql:8.0


docker exec -it my-mysql mysql -u root -p