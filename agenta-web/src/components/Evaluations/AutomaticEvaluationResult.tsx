import {
    deleteEvaluations,
    fetchEvaluationResults,
    fetchAllLoadEvaluations,
} from "@/services/human-evaluations/api"
import {Button, Spin, Statistic, Table, Typography} from "antd"
import {useRouter} from "next/router"
import {useEffect, useState} from "react"
import {ColumnsType} from "antd/es/table"
import {Evaluation, SingleModelEvaluationListTableDataType, StyleProps} from "@/lib/Types"
import {DeleteOutlined} from "@ant-design/icons"
import {EvaluationFlow, EvaluationType} from "@/lib/enums"
import {createUseStyles} from "react-jss"
import {useAppTheme} from "../Layout/ThemeContextProvider"
import {calculateResultsDataAvg} from "@/lib/helpers/evaluate"
import {
    fromEvaluationResponseToEvaluation,
    singleModelTestEvaluationTransformer,
} from "@/lib/transformers"
import {variantNameWithRev} from "@/lib/helpers/variantHelper"

const useStyles = createUseStyles({
    container: {
        marginBottom: 20,
    },
    collapse: ({themeMode}: StyleProps) => ({
        margin: "10px 0",
        "& .ant-collapse-header": {
            alignItems: "center !important",
            padding: "0px 20px !important",
            borderTopLeftRadius: "10px !important",
            borderTopRightRadius: "10px !important",
            background: themeMode === "dark" ? "#1d1d1d" : "#f8f8f8",
        },
    }),
    stat: {
        "& .ant-statistic-content-value": {
            fontSize: 20,
            color: "#1677ff",
        },
        "& .ant-statistic-content-suffix": {
            fontSize: 20,
            color: "#1677ff",
        },
    },
    btnContainer: {
        display: "flex",
        alignItems: "center",
        justifyContent: "flex-end",
        margin: "20px 0",
        gap: 10,
        "& svg": {
            color: "red",
        },
    },
})

const {Title} = Typography
interface AutomaticEvaluationResultProps {
    setIsEvalModalOpen: React.Dispatch<React.SetStateAction<boolean>>
}
export default function AutomaticEvaluationResult({
    setIsEvalModalOpen,
}: AutomaticEvaluationResultProps) {
    const router = useRouter()
    const [evaluationsList, setEvaluationsList] = useState<
        SingleModelEvaluationListTableDataType[]
    >([])
    const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([])
    const [selectionType] = useState<"checkbox" | "radio">("checkbox")
    const {appTheme} = useAppTheme()
    const classes = useStyles({themeMode: appTheme} as StyleProps)
    const app_id = router.query.app_id?.toString() || ""
    const [fetchingEvaluations, setFetchingEvaluations] = useState(false)

    useEffect(() => {
        if (!app_id) {
            return
        }

        const fetchEvaluations = async () => {
            try {
                setFetchingEvaluations(true)
                const evals: Evaluation[] = (await fetchAllLoadEvaluations(app_id)).map(
                    fromEvaluationResponseToEvaluation,
                )
                const results = await Promise.all(evals.map((e) => fetchEvaluationResults(e.id)))
                const newEvals = results.map((result, ix) => {
                    const item = evals[ix]
                    if ([EvaluationType.single_model_test].includes(item.evaluationType)) {
                        return singleModelTestEvaluationTransformer({item, result})
                    }
                })

                setEvaluationsList(
                    newEvals
                        .filter((evaluation) => evaluation !== undefined)
                        .filter(
                            (item: any) =>
                                item.resultsData !== undefined ||
                                !(Object.keys(item.scoresData || {}).length === 0) ||
                                item.avgScore !== undefined,
                        ) as any,
                )
            } catch (error) {
                console.error(error)
            } finally {
                setFetchingEvaluations(false)
            }
        }

        fetchEvaluations()
    }, [app_id])

    const handleNavigation = (variantName: string, revisionNum: string) => {
        router.push(`/apps/${app_id}/playground?variant=${variantName}&revision=${revisionNum}`)
    }

    const onCompleteEvaluation = (evaluation: any) => {
        // TODO: improve type
        const evaluationType =
            EvaluationType[evaluation.evaluationType as keyof typeof EvaluationType]

        if (evaluationType === EvaluationType.single_model_test) {
            router.push(`/apps/${app_id}/annotations/single_model_test/${evaluation.key}`)
        }
    }

    const columns: ColumnsType<SingleModelEvaluationListTableDataType> = [
        {
            title: "Variant",
            dataIndex: "variants",
            key: "variants",
            render: (value, record: SingleModelEvaluationListTableDataType) => {
                return (
                    <div
                        onClick={() => handleNavigation(value[0].variantName, record.revisions[0])}
                        style={{cursor: "pointer"}}
                    >
                        <span>
                            {variantNameWithRev({
                                variant_name: value[0].variantName,
                                revision: record.revisions[0],
                            })}
                        </span>
                    </div>
                )
            },
        },
        {
            title: "Test set",
            dataIndex: "testsetName",
            key: "testsetName",
            render: (value: any, record: SingleModelEvaluationListTableDataType, index: number) => {
                return <span>{record.testset.name}</span>
            },
        },
        {
            title: "Average score",
            dataIndex: "averageScore",
            key: "averageScore",
            render: (value: any, record: SingleModelEvaluationListTableDataType, index: number) => {
                let score = 0
                if (record.scoresData) {
                    score =
                        ((record.scoresData.correct?.length ||
                            record.scoresData.true?.length ||
                            0) /
                            record.scoresData.nb_of_rows) *
                        100
                } else if (record.resultsData) {
                    const multiplier = {
                        [EvaluationType.auto_webhook_test]: 100,
                        [EvaluationType.single_model_test]: 1,
                    }
                    score = calculateResultsDataAvg(
                        record.resultsData,
                        multiplier[record.evaluationType as keyof typeof multiplier],
                    )
                    score = isNaN(score) ? 0 : score
                } else if (record.avgScore) {
                    score = record.avgScore * 100
                }

                return (
                    <span>
                        <Statistic
                            className={classes.stat}
                            value={score}
                            precision={score <= 99 ? 2 : 1}
                            suffix="%"
                        />
                    </span>
                )
            },
        },
        {
            title: "Created at",
            dataIndex: "createdAt",
            key: "createdAt",
            width: "300",
        },
        {
            title: "Action",
            dataIndex: "action",
            key: "action",
            render: (value: any, record: SingleModelEvaluationListTableDataType, index: number) => {
                let actionText = "View evaluation"
                if (record.status !== EvaluationFlow.EVALUATION_FINISHED) {
                    actionText = "Continue evaluation"
                }
                return (
                    <div className="hover-button-wrapper">
                        <Button
                            type="primary"
                            data-cy="single-model-view-evaluation-button"
                            onClick={() => onCompleteEvaluation(record)}
                        >
                            {actionText}
                        </Button>
                    </div>
                )
            },
        },
    ]

    const rowSelection = {
        onChange: (
            selectedRowKeys: React.Key[],
            selectedRows: SingleModelEvaluationListTableDataType[],
        ) => {
            setSelectedRowKeys(selectedRowKeys)
        },
    }

    const onDelete = async () => {
        const evaluationsIds = selectedRowKeys.map((key) => key.toString())
        try {
            await deleteEvaluations(evaluationsIds)
            setEvaluationsList((prevEvaluationsList) =>
                prevEvaluationsList.filter(
                    (evaluation) => !evaluationsIds.includes(evaluation.key),
                ),
            )

            setSelectedRowKeys([])
        } catch (error) {
            console.error(error)
        }
    }

    return (
        <div>
            <div className={classes.btnContainer}>
                <Button onClick={onDelete} disabled={selectedRowKeys.length == 0}>
                    <DeleteOutlined key="delete" />
                    Delete
                </Button>
                <Button
                    type="primary"
                    data-cy="new-annotation-modal-button"
                    onClick={() => setIsEvalModalOpen(true)}
                >
                    New Evaluation
                </Button>
            </div>

            <div className={classes.container}>
                <Title level={3}>Single Model Test Results</Title>
            </div>

            <Spin spinning={fetchingEvaluations}>
                <Table
                    rowSelection={{
                        type: selectionType,
                        ...rowSelection,
                    }}
                    className="ph-no-capture"
                    data-cy="automatic-evaluation-result"
                    columns={columns}
                    dataSource={evaluationsList}
                />
            </Spin>
        </div>
    )
}
