SELECT 
	"departmentId" AS department_id
  , "departmentName" AS department_name	
FROM
	{{ source('main', 'departments') }}