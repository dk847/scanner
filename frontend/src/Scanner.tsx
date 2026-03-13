import { useState } from 'react'

import { STYLES } from './styles'
import { API_URL } from './constants'


interface FormDataInterface {
    file: File | null
    advisories_to_ignore: string
    is_json: boolean
}

const Scanner = () => {
    const [formData, setFormData] = useState<FormDataInterface>({
        file: null,
        advisories_to_ignore: '',
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
        fd.append('advisories_to_ignore', formData.advisories_to_ignore)
        fd.append('is_json', formData.is_json.toString())

        fetch(API_URL, { method: 'POST', body: fd })
            .then((resp) => resp.text())
            .then((data) => setOutput(data))
            .catch(() => setError('Failed to scan manifest. Please try again.'))
            .finally(() => setIsSubmitting(false))
    }

    const getButtonStyles = () => {
        if (isSubmitting) {
            return  { ...STYLES.button, ...STYLES.buttonDisabled}
        }
        return { ...STYLES.button }
    }

    return (
        <form style={STYLES.form} onSubmit={(e) => handleSubmit(e)}>
            <div style={STYLES.inputContainer}>
                <label style={STYLES.label}>File</label>
                <input
                    type='file'
                    onChange={(e) => handleFileUpload(e)}
                    style={STYLES.fileInput}
                    required
                    disabled={isSubmitting}
                />
            </div>

            <div style={STYLES.inputContainer}>
                <label style={STYLES.label}>Advisories to Ignore</label>
                <textarea
                    onChange={(e) => setFormData((prev) => (
                        { ...prev, advisories_to_ignore: e.target.value }
                    ))}
                    style={STYLES.textArea}
                    placeholder='CVE-2022-37603, CVE-2022-37601, CVE-2022-37599'
                    rows={5}
                    disabled={isSubmitting}
                />
            </div>

            <div style={STYLES.inputContainer}>
                <label style={ STYLES.label }>Is JSON</label>
                <input
                    type='checkbox'
                    checked={formData.is_json}
                    onChange={(e) => {
                        setFormData((prev) => ({ ...prev, is_json: e.target.checked }))
                    }}
                    disabled={isSubmitting}
                />
            </div>

            <button
                style={getButtonStyles()}
                type='submit'
                disabled={isSubmitting}
            >
                Submit
            </button>

            <div style={STYLES.output}>
                {error && <p style={STYLES.error}>{error}</p>}
                {isSubmitting ? <p>Scanning manifest...</p> : <pre>{output}</pre>}
            </div>
        </form>
    )
}

export default Scanner
