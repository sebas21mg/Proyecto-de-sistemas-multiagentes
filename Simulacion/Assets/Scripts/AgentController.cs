﻿// TC2008B. Sistemas Multiagentes y Gráficas Computacionales
// C# client to interact with Python. Based on the code provided by Sergio Ruiz.
// Octavio Navarro. October 2023

using System;
using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;

[Serializable]
public class AgentData
{
    /*
    The AgentData class is used to store the data of each agent.
    
    Attributes:
        id (string): The id of the agent.
        x (float): The x coordinate of the agent.
        y (float): The y coordinate of the agent.
        z (float): The z coordinate of the agent.
    */
    public string id;
    public float x, y, z, destX, destZ;

    public AgentData(string id, float x, float y, float z, float destX, float destZ)
    {
        this.id = id;
        this.x = x;
        this.y = y;
        this.z = z;
        this.destX = destX;
        this.destZ = destZ;
    }
}

[Serializable]

public class AgentsData
{
    /*
    The AgentsData class is used to store the data of all the agents.

    Attributes:
        positions (list): A list of AgentData objects.
    */
    public List<AgentData> positions;

    public AgentsData() => this.positions = new List<AgentData>();
}

public class AgentController : MonoBehaviour
{
    /*
    The AgentController class is used to control the agents in the simulation.

    Attributes:
        serverUrl (string): The url of the server.
        getAgentsEndpoint (string): The endpoint to get the agents data.
        getObstaclesEndpoint (string): The endpoint to get the obstacles data.
        sendConfigEndpoint (string): The endpoint to send the configuration.
        updateEndpoint (string): The endpoint to update the simulation.
        agentsData (AgentsData): The data of the agents.
        obstacleData (AgentsData): The data of the obstacles.
        agents (Dictionary<string, GameObject>): A dictionary of the agents.
        prevPositions (Dictionary<string, Vector3>): A dictionary of the previous positions of the agents.
        currPositions (Dictionary<string, Vector3>): A dictionary of the current positions of the agents.
        updated (bool): A boolean to know if the simulation has been updated.
        started (bool): A boolean to know if the simulation has started.
        agentPrefab (GameObject): The prefab of the agents.
        obstaclePrefab (GameObject): The prefab of the obstacles.
        floor (GameObject): The floor of the simulation.
        NAgents (int): The number of agents.
        width (int): The width of the simulation.
        height (int): The height of the simulation.
        timeToUpdate (float): The time to update the simulation.
        timer (float): The timer to update the simulation.
        dt (float): The delta time.
    */
    string serverUrl = "http://localhost:8585";
    string getAgentsEndpoint = "/getCars";
    string getObstaclesEndpoint = "/getObstacles";
    string getTrafficLightsEndpoint = "/getTrafficLights";
    string getRoadsEndpoint = "/getRoad";
    string getDestinationsEndpoint = "/getDestination";
    string sendConfigEndpoint = "/init";
    string updateEndpoint = "/update";
    AgentsData agentsData, obstacleData, trafficLightsData, roadsData, destinationsData;
    Dictionary<string, GameObject> agents;
    Dictionary<string, Vector3> prevPositions, currPositions, prevDirections;

    bool updated = false, started = false;

    public GameObject agentPrefab, obstaclePrefab, trafficLightPrefab, roadPrefab, destinationPrefab;
    public float timeToUpdate = 5.0f;
    private float timer, dt;

    void Start()
    {
        agentsData = new AgentsData();
        obstacleData = new AgentsData();
        trafficLightsData = new AgentsData();
        roadsData = new AgentsData();
        destinationsData = new AgentsData();

        // Initializes the dictionaries to store the agents positions.
        // prevPositions stores the previous positions of the agents, while currPositions stores the current positions.
        prevPositions = new Dictionary<string, Vector3>();
        currPositions = new Dictionary<string, Vector3>();
        prevDirections = new Dictionary<string, Vector3>();

        agents = new Dictionary<string, GameObject>();

        // Sets the floor scale and position.
        // floor.transform.localScale = new Vector3((float)width / 10, 1, (float)height / 10);
        // floor.transform.localPosition = new Vector3((float)width / 2 - 0.5f, 0, (float)height / 2 - 0.5f);

        timer = timeToUpdate;

        // Launches a couroutine to send the configuration to the server.
        StartCoroutine(SendConfiguration());
    }

    private void Update()
    {
        if (timer < 0)
        {
            timer = timeToUpdate;
            updated = false;
            StartCoroutine(UpdateSimulation());
        }

        if (updated)
        {
            timer -= Time.deltaTime;
            dt = 1.0f - (timer / timeToUpdate);

            // Iterates over the agents to update their positions. 
            // The positions are interpolated between the previous and current positions.
            foreach (var agent in currPositions)
            {
                Vector3 currentPosition = agent.Value;
                Vector3 previousPosition = prevPositions[agent.Key];

                Vector3 interpolated = Vector3.Lerp(previousPosition, currentPosition, dt);

                Vector3 direction = currentPosition - previousPosition;
                if (direction == new Vector3(0, 0, 0))
                    direction = prevDirections[agent.Key];
                else
                    prevDirections[agent.Key] = direction;

                agents[agent.Key].gameObject.GetComponent<ApplyTransforms>().displacement = interpolated + new Vector3(0, -1, 1);
                agents[agent.Key].gameObject.GetComponent<ApplyTransforms>().rotation = direction;

            }

        }
    }

    IEnumerator UpdateSimulation()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + updateEndpoint);
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            StartCoroutine(GetCarsData());
        }
    }

    IEnumerator SendConfiguration()
    {
        /*
        The SendConfiguration method is used to send the configuration to the server.

        It uses a WWWForm to send the data to the server, and then it uses a UnityWebRequest to send the form.
        */
        WWWForm form = new WWWForm();

        // form.AddField("width", width.ToString());
        // form.AddField("height", height.ToString());

        UnityWebRequest www = UnityWebRequest.Post(serverUrl + sendConfigEndpoint, form);
        www.SetRequestHeader("Content-Type", "application/x-www-form-urlencoded");

        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
        }
        else
        {
            // Debug.Log("Configuration upload complete!");
            // Debug.Log("Getting Agents positions");

            // Once the configuration has been sent, it launches a coroutine to get the agents data.
            StartCoroutine(GetCarsData());
            StartCoroutine(GetObstacleData());
            StartCoroutine(GetTrafficLightsData());
            StartCoroutine(GetRoadsData());
            StartCoroutine(GetDestinationsData());
        }
    }

    IEnumerator GetCarsData()
    {
        // The GetCarsData method is used to get the agents data from the server.

        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getAgentsEndpoint);
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);

        else
        {
            // Once the data has been received, it is stored in the agentsData variable.
            // Then, it iterates over the agentsData.positions list to update the agents positions.
            agentsData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);

            foreach (AgentData agent in agentsData.positions)
            {
                Vector3 newAgentPosition = new Vector3(agent.x, agent.y, agent.z);
                Vector3 destination = new Vector3(agent.destX, agent.y, agent.destZ);

                if (!prevPositions.ContainsKey(agent.id))
                {
                    prevPositions[agent.id] = newAgentPosition;
                    prevDirections[agent.id] = new Vector3(1, 0, 0);
                    agents[agent.id] = Instantiate(agentPrefab, new Vector3(0, 0, -1), Quaternion.identity);
                }
                else
                {
                    Vector3 currentPosition = new Vector3();
                    if (currPositions.TryGetValue(agent.id, out currentPosition))
                        prevPositions[agent.id] = currentPosition;
                    currPositions[agent.id] = newAgentPosition;

                    if (newAgentPosition == destination)
                    {
                        GameObject toDestroy = agents[agent.id];

                        foreach (Transform child in toDestroy.transform)
                        {
                            Destroy(child.gameObject);
                        }

                        Destroy(toDestroy);
                        agents.Remove(agent.id);
                        prevPositions.Remove(agent.id);
                        currPositions.Remove(agent.id);
                        prevDirections.Remove(agent.id);
                    }
                }
            }

            updated = true;
            if (!started) started = true;
        }
    }

    IEnumerator GetObstacleData()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getObstaclesEndpoint);
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            obstacleData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);

            // Debug.Log(obstacleData.positions);

            foreach (AgentData obstacle in obstacleData.positions)
            {
                Instantiate(obstaclePrefab, new Vector3(obstacle.x, obstacle.y, obstacle.z), Quaternion.identity);
            }
        }
    }

    IEnumerator GetTrafficLightsData()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getTrafficLightsEndpoint);
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            trafficLightsData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);

            // Debug.Log(trafficLightsData.positions);

            foreach (AgentData trafficLight in trafficLightsData.positions)
            {
                Instantiate(trafficLightPrefab, new Vector3(trafficLight.x, trafficLight.y, trafficLight.z), Quaternion.identity);
            }
        }
    }

    IEnumerator GetRoadsData()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getRoadsEndpoint);
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            roadsData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);

            // Debug.Log(roadsData.positions);

            foreach (AgentData road in roadsData.positions)
            {
                Instantiate(roadPrefab, new Vector3(road.x, road.y, road.z), Quaternion.identity);
            }
        }
    }

    IEnumerator GetDestinationsData()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getDestinationsEndpoint);
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            destinationsData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);

            // Debug.Log(destinationsData.positions);

            foreach (AgentData destination in destinationsData.positions)
            {
                Instantiate(destinationPrefab, new Vector3(destination.x, destination.y, destination.z), Quaternion.identity);
            }
        }
    }
}
