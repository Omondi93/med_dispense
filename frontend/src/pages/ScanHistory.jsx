import { useEffect, useState } from "react";

import DashboardLayout
from "../layouts/DashboardLayout";

import {
    getScanHistory
}
from "../services/scanService";


function ScanHistory(){

    const [logs,setLogs]=useState([]);

    const [loading,setLoading]=useState(true);


    useEffect(()=>{

        loadHistory();

    },[]);


    const loadHistory = async()=>{

        try{

            const data =
            await getScanHistory();

            setLogs(
                data.data
            );

        }

        catch(error){

            console.log(error);

        }

        finally{

            setLoading(false);

        }

    };


return(

<DashboardLayout>

<h1 className="text-4xl font-bold mb-6">

Scan History

</h1>


{loading ? (

<p>Loading...</p>

) : (

<div className="bg-white rounded-xl shadow overflow-hidden">

<table className="w-full">

<thead className="bg-black text-white">

<tr>

<th className="p-4">
Batch
</th>

<th className="p-4">
Status
</th>

<th className="p-4">
Count
</th>

<th className="p-4">
Time
</th>

<th className="p-4">
IP
</th>

</tr>

</thead>

<tbody>

{
logs.map(
(log,index)=>(

<tr
key={index}
className="border-b"
>

<td className="p-4">
{log.batch_id}
</td>

<td className="p-4">
{log.status}
</td>

<td className="p-4">
{log.scan_count}
</td>

<td className="p-4">
{log.scanned_at}
</td>

<td className="p-4">
{log.ip_address}
</td>

</tr>

))
}

</tbody>

</table>

</div>

)}

</DashboardLayout>

)

}

export default ScanHistory;