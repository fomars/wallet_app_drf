### Task:

Develop REST API server using django-rest-framework with pagination, sorting and filtering for two models:

**Transaction** _(id, wallet_id (fk), txid, amount)_:

 - **txid** is required unique string field, 
 - **amount** is a number with 18-digits precision. Transaction amount may be negative.

**Wallet** _(id, label, balance)_;
 
 - **label** is a string field
 - **balance** is a summary of all transactions’s amounts.  Wallet balance should NEVER be negative


Will be your advantage:

Test coverage
Any linter usage
Quick start app guide if you create your own docker-compose or Dockerfiles
Comments in non-standart places in code
Use database indexes if you think it's advisable