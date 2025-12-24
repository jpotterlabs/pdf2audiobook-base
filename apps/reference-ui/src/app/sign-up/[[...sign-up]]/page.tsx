import { SignUp } from '@clerk/nextjs'

export function generateStaticParams() {
  return [{ 'sign-up': [] }]
}

export default function SignUpPage() {
  return (
    <div className="flex justify-center items-center h-screen">
      <SignUp />
    </div>
  )
}
