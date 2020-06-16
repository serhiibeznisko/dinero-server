# Requirements to start project
    - docker
    - docker-compose 

Recommended, but not needed:

    - Linux System
    - make
    
 
# Development
    - make run
    - make migrate
    - make populatedb

If you don't have make program in your system, copy commands manually from Makefile and write them into your terminal.

After that you will have fully working development environment with initial sample campaign.

Try to log in to http://localhost:8001/management/admin with your previously created admin credentials and check out how it does work. 
    
# Server setup
    You need to login with aws-cli and heroku cli on your local computer.
    - Install terraform
    - terraform init
    # Staging ENV
    - terraform workspace new staging
    - terraform apply
    # Production ENV
    - terraform workspace new production
    - terraform apply
    
Terraform will try to connect heroku pipeline which we created on staging workspace with production dyno which will fail. To fix that, please edit manually production workspace terraform state after deployment and change heroku_pipeline id resource to the one from staging workspace. 
    
After deployment you will need to put manually keys into heroku dyno envs for https://grabz.it and https://tpay.com.    

TIP: Create superuser admin after deployment with going to ash shell on Heroku and type python src/manage.py createsuperuser

It will setup whole server solution with Heroku Django hosting, Heroku Postgres, and AWS S3 with CDN CloudFront.
