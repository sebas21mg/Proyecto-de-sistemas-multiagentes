using System.Collections;
using System.Collections.Generic;
// using Unity.VisualScripting;
using UnityEngine;

public class ApplyTransforms : MonoBehaviour
{
    [SerializeField] public Vector3 rotation;
    [SerializeField] public Vector3 displacement;
    [SerializeField] float spinSpeed;
    [SerializeField] AXIS rotationAxis;
    [SerializeField] GameObject wheelPrefab;

    Transform car;
    float rotationAngle;
    GameObject[] wheels;
    Mesh[] meshes;
    Vector3[][] baseVertices;
    Vector3[][] newVertices;
    Vector3[] wheelsPos = new Vector3[4];


    // Start is called before the first frame update
    void Start()
    {
        wheels = new GameObject[4];
        car = gameObject.transform;
        InstanciarObjeto();

        meshes = new Mesh[5];
        baseVertices = new Vector3[5][];
        newVertices = new Vector3[5][];

        meshes[0] = GetComponentInChildren<MeshFilter>().mesh;
        for (int i = 1; i < 5; i++)
        {
            meshes[i] = wheels[i - 1].GetComponentInChildren<MeshFilter>().mesh;
        }

        for (int i = 0; i < meshes.Length; i++)
        {
            baseVertices[i] = meshes[i].vertices;

            newVertices[i] = new Vector3[baseVertices[i].Length];
            for (int j = 0; j < baseVertices.Length; j++)
            {
                newVertices[i][j] = baseVertices[i][j];
            }
        }
    }

    // Update is called once per frame
    void Update()
    {
        DoTransform();
    }

    void DoTransform()
    {
        rotationAngle = Mathf.Atan2(rotation.z, rotation.x) * Mathf.Rad2Deg - 90;

        Matrix4x4 move = HW_Transforms.TranslationMat(displacement.x,
                                                        displacement.y,
                                                        displacement.z);

        Matrix4x4 rotate = HW_Transforms.RotateMat(rotationAngle, rotationAxis);

        Matrix4x4 spin = HW_Transforms.RotateMat(spinSpeed * Time.time, AXIS.X);

        Matrix4x4 scale = HW_Transforms.ScaleMat(0.2f, 0.2f, 0.2f);

        for (int i = 0; i < meshes.Length; i++)
        {
            Matrix4x4 composite;

            if (i > 0)
            {
                Matrix4x4 goToOrigin = HW_Transforms.TranslationMat(-wheelsPos[i - 1].x,
                                                                    0,
                                                                    -wheelsPos[i - 1].z);

                Matrix4x4 goBackToPlace = HW_Transforms.TranslationMat(wheelsPos[i - 1].x,
                                                                        0,
                                                                        wheelsPos[i - 1].z);

                composite = move * goToOrigin * rotate * goBackToPlace * spin;
            }
            else
                composite = move * rotate * scale;

            for (int j = 0; j < baseVertices[i].Length; j++)
            {
                Vector4 temp = new Vector4(baseVertices[i][j].x,
                                            baseVertices[i][j].y,
                                            baseVertices[i][j].z,
                                            1);

                newVertices[i][j] = composite * temp;
            }

            meshes[i].vertices = newVertices[i];
            meshes[i].RecalculateNormals();
        }

    }

    void InstanciarObjeto()
    {
        float x = 0.127f, y = 0.065f, z = 0.246f;

        wheelsPos[0] = new Vector3(x, y, z);
        wheelsPos[1] = new Vector3(-x, y, z);
        wheelsPos[2] = new Vector3(x, y, -z);
        wheelsPos[3] = new Vector3(-x, y, -z);

        for (int i = 0; i < 4; i++)
        {
            Vector3 relativePos = car.position + wheelsPos[i];
            wheels[i] = Instantiate(wheelPrefab, relativePos, Quaternion.identity);
            wheels[i].transform.parent = transform;
        }
    }
}