-- Roda sozinho na primeira subida do container.
-- O banco principal (liga_sudoers_dw) e criado pelo proprio Docker.
-- Aqui so nasce o transacional, que serve de ORIGEM para a carga do DW.
CREATE DATABASE liga_sudoers OWNER sudoers;
