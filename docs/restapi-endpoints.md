#  REST API Endpoints
This section provides a detailed list of avaliable endpoints in Controller REST API.

## Prepare environment 
  Sets the amount of resources allocated to instances.

* **URL**: `/setup`
* **Method:** `POST`

* **JSON Request:**
	* ```javascript
	  {
	     actuator_plugin: [string],
	     instances_cap : {
	       "vm_id0":cap0,
	       "vm_id1":cap1,
	       ...
	       "vm_idn":capn
	     }
	  }
	  ```
* **Success Response:**
  * **Code:** `204` <br />
		
* **Error Response:**
  * **Code:** `400 BAD REQUEST`

## Start scaling 
  Adds the application to the set of applications the Controller scales.

* **URL**: `/scaling/:app_id`
* **Method:** `POST`

* **JSON Request:**
	* ```javascript
	  {
	     plugin: [string],
	     plugin_info : {
	       ...
	     }
	  }
	  ```
* **Success Response:**
  * **Code:** `204` <br />
		
* **Error Response:**
  * **Code:** `400 BAD REQUEST`

## Stop scaling 
  Removes the application from the set of applications the Controller scales.

* **URL**: `/scaling/:app_id/stop`
* **Method:** `PUT`

* **Success Response:**
  * **Code:** `204` <br />
		
* **Error Response:**
  * **Code:** `400 BAD REQUEST`<br />

## Controller status
  Returns json data with detailed status of Controller.

* **URL**: `/scaling`
* **Method:** `GET`
* **Success Response:**
  * **Code:** `200` <br /> **Content:** 
	  * ```javascript
	    {
	       scaling1 : {
	          status: [string]
	       },
     	       ...
	       scalingN : {
	          status: [string]
	       }		 
	    }
		```

## Add cluster
  Add a new cluster reference into the Asperathos Controller section

* **URL**: `/cluster`
* **Method:** `POST`
* **JSON Request:**
	* ```javascript
		{
			"user" : [string],
			"password" : [string],
			"cluster_name" : [string],
			"cluster_config" : [string]
		}
* **Success Response:**
  * **Code:** `220` <br /> **Content:** 
	  * ```javascript
	    {
			"cluster_name" : [string],
			"status": [string],
			"reason": [string]
	    }
		```

## Add certificate
  Add a certificate in the a cluster reference into the Asperathos Controller section

* **URL**: `/cluster/:cluster_name`
* **Method:** `POST`
* **JSON Request:**
	* ```javascript
		{
			"user" : [string],
			"password" : [string],
			"certificate_name" : [string],
			"certificate_content" : [string]
		}
* **Success Response:**
  * **Code:** `220` <br /> **Content:** 
	  * ```javascript
	    {
			"cluster_name" : [string],
			"certificate_name" : [string],
			"status": [string],
			"reason": [string]
	    }
		```

## Delete cluster
  Delete a cluster reference of the Asperathos Controller section

* **URL**: `/cluster/:app_id/delete`
* **Method:** `POST`
* **JSON Request:**
	* ```javascript
		{
			"user" : [string],
			"password" : [string]
		}
* **Success Response:**
  * **Code:** `220` <br /> **Content:** 
	  * ```javascript
	    {
			"cluster_name" : [string],
			"status": [string],
			"reason": [string]
	    }
		```

## Delete certificate
  Delete a certificate of a cluster reference in the Asperathos Controller section

* **URL**: `/cluster/:cluster_name/certificate/:certificate_name/delete`
* **Method:** `POST`
* **JSON Request:**
	* ```javascript
		{
			"user" : [string],
			"password" : [string]
		}
* **Success Response:**
  * **Code:** `220` <br /> **Content:** 
	  * ```javascript
	    {
			"cluster_name" : [string],
			"certificate_name" : [string],
			"status": [string],
			"reason": [string]
	    }
		```

## Active cluster
  Start to use the informed cluster as active cluster in the Asperathos Controller section.

* **URL**: `/cluster/:app_id`
* **Method:** `POST`
* **JSON Request:**
	* ```javascript
		{
			"user" : [string],
			"password" : [string]
		}
* **Success Response:**
  * **Code:** `220` <br /> **Content:** 
	  * ```javascript
	    {
			"cluster_name" : [string],
			"status": [string],
			"reason": [string]
	    }
		```
		