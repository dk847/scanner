import { useState } from "react"

import * as STYLES from './styles'
import { API_URL } from "./constants"


interface FormDataInterface {
    file: File | null
    is_json: boolean
}

const Scanner = () => {
    const [formData, setFormData] = useState<FormDataInterface>({
        file: null,
        is_json: false,
    })
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [output, setOutput] = useState('')
    const [error, setError] = useState('')

    const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files
        if (files && files.length > 0) {
            setFormData((prev) => ({ ...prev, file: files[0]}))
        }
    }

    const handleSubmit = (e: React.SubmitEvent<HTMLFormElement>) => {
        e.preventDefault()

        setOutput('')
        setError('')

        if (formData.file === null) {
            return
        }

        setIsSubmitting(true)

        const fd = new FormData()
        fd.append('file', formData.file)
        fd.append('is_json', formData.is_json.toString())

        fetch(API_URL, { method: 'POST', body: fd })
            .then((resp) => resp.text())
            .then((data) => setOutput(data))
            .catch(() => setError('Failed to scan manifest. Please try again.'))
            .finally(() => setIsSubmitting(false))
    }

    return (
        <form style={STYLES.default.form} onSubmit={(e) => handleSubmit(e)}>
            <div style={STYLES.default.inputContainer}>
                <label style={STYLES.default.label}>File</label>
                <input
                    type='file'
                    onChange={(e) => handleFileUpload(e)}
                    style={STYLES.default.fileInput}
                    required
                />
            </div>

            <div style={STYLES.default.inputContainer}>
                <label style={STYLES.default.label}>Is JSON</label>
                <input
                    type='checkbox'
                    checked={formData.is_json}
                    onChange={(e) => {
                        setFormData((prev) => ({ ...prev, is_json: e.target.checked }))
                    }}
                />
            </div>

            <button
                type="submit"
                disabled={isSubmitting}
                style={STYLES.default.button}
            >
                Submit
            </button>

            <div style={STYLES.default.output}>
                {error && <p style={STYLES.default.error}>{error}</p>}
                {isSubmitting ? <p>Scanning manifest...</p> : <pre>{output}</pre>}
            </div>
        </form>
    )
}

export default Scanner
