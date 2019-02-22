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
