import type { FormEvent, ReactNode } from "react";
import { useState } from "react";
import { Check, Clock, FileUp, MapPin, Save, Trash2 } from "lucide-react";
import { useAuth } from "@/auth/useAuth";
import { ErrorState } from "@/components/states/ErrorState";
import { LoadingState } from "@/components/states/LoadingState";
import { PageHeader } from "@/components/layout/PageHeader";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  useAvailability,
  useChangeAvailability,
  useCreateAvailability,
  useCredentials,
  useDeleteAvailability,
  useNurseProfile,
  useReplaceProfileSpecializations,
  useSpecializations,
  useUpdateNurseProfile,
  useUploadCredential,
} from "@/hooks/useNurses";
import {
  useCreateDependent,
  useCreateEmergencyContact,
  useDeleteDependent,
  useDeleteEmergencyContact,
  useDependents,
  useEmergencyContacts,
  usePatientProfile,
  useUpdatePatientProfile,
} from "@/hooks/usePatient";
import { useGeolocation } from "@/hooks/useGeolocation";
import { useUpdateLocation } from "@/hooks/useLocation";
import type { Gender, NurseStatus, PatientProfilePatch } from "@/types";
import { getUserErrorMessage } from "@/utils/errors";

const inputClass = "h-10 w-full rounded-md border border-input bg-background px-3 text-sm";
const textareaClass =
  "min-h-24 w-full rounded-md border border-input bg-background px-3 py-2 text-sm";

function formValue(form: HTMLFormElement, name: string): string {
  const value = new FormData(form).get(name);
  return typeof value === "string" ? value : "";
}

function PatientProfilePanel(): ReactNode {
  const profile = usePatientProfile(true);
  const updateProfile = useUpdatePatientProfile();
  const contacts = useEmergencyContacts();
  const createContact = useCreateEmergencyContact();
  const deleteContact = useDeleteEmergencyContact();
  const dependents = useDependents();
  const createDependent = useCreateDependent();
  const deleteDependent = useDeleteDependent();
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function saveProfile(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setMessage(null);
    setError(null);
    const form = event.currentTarget;
    const payload: PatientProfilePatch = {
      phone_number: formValue(form, "phone_number"),
      national_id: formValue(form, "national_id"),
      gender: formValue(form, "gender") as PatientProfilePatch["gender"],
      date_of_birth: formValue(form, "date_of_birth"),
      blood_group: formValue(form, "blood_group"),
      county: formValue(form, "county"),
      address: formValue(form, "address"),
      allergies: formValue(form, "allergies"),
      chronic_conditions: formValue(form, "chronic_conditions"),
      current_medications: formValue(form, "current_medications"),
      disabilities: formValue(form, "disabilities"),
      medical_notes: formValue(form, "medical_notes"),
    };
    try {
      await updateProfile.mutateAsync(payload);
      setMessage("Patient profile saved.");
    } catch (requestError) {
      setError(getUserErrorMessage(requestError));
    }
  }

  async function addContact(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    const form = event.currentTarget;
    await createContact.mutateAsync({
      name: formValue(form, "name"),
      phone_number: formValue(form, "phone_number"),
      relationship: formValue(form, "relationship"),
    });
    form.reset();
  }

  async function addDependent(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    const form = event.currentTarget;
    await createDependent.mutateAsync({
      full_name: formValue(form, "full_name"),
      date_of_birth: formValue(form, "date_of_birth"),
      gender: formValue(form, "gender") as Gender,
      relationship: formValue(form, "relationship"),
      medical_notes: formValue(form, "medical_notes"),
    });
    form.reset();
  }

  if (profile.isLoading) return <LoadingState />;
  if (profile.error || !profile.data) {
    return <ErrorState message="Patient profile could not be loaded." />;
  }

  return (
    <div className="grid gap-4 xl:grid-cols-[minmax(0,1.3fr)_minmax(320px,0.7fr)]">
      <Card>
        <CardHeader>
          <CardTitle>Medical Profile</CardTitle>
        </CardHeader>
        <CardContent>
          <form className="grid gap-4 md:grid-cols-2" onSubmit={(event) => void saveProfile(event)}>
            <Field name="phone_number" label="Phone" defaultValue={profile.data.phone_number} />
            <Field name="national_id" label="National ID" defaultValue={profile.data.national_id} />
            <Select name="gender" label="Gender" defaultValue={profile.data.gender}>
              <option value="">Select gender</option>
              <option value="FEMALE">Female</option>
              <option value="MALE">Male</option>
              <option value="OTHER">Other</option>
            </Select>
            <Field name="date_of_birth" label="Date of birth" type="date" defaultValue={profile.data.date_of_birth} />
            <Field name="blood_group" label="Blood group" defaultValue={profile.data.blood_group} />
            <Field name="county" label="County" defaultValue={profile.data.county} />
            <div className="md:col-span-2">
              <TextArea name="address" label="Address" defaultValue={profile.data.address} />
            </div>
            <TextArea name="allergies" label="Allergies" defaultValue={profile.data.allergies} />
            <TextArea name="chronic_conditions" label="Chronic conditions" defaultValue={profile.data.chronic_conditions} />
            <TextArea name="current_medications" label="Current medications" defaultValue={profile.data.current_medications} />
            <TextArea name="disabilities" label="Disabilities" defaultValue={profile.data.disabilities} />
            <div className="md:col-span-2">
              <TextArea name="medical_notes" label="Medical notes" defaultValue={profile.data.medical_notes} />
            </div>
            {message ? <p className="text-sm text-emerald-700 md:col-span-2">{message}</p> : null}
            {error ? <p className="text-sm text-destructive md:col-span-2">{error}</p> : null}
            <Button className="md:col-span-2" type="submit" disabled={updateProfile.isPending}>
              <Save className="h-4 w-4" aria-hidden="true" />
              Save Profile
            </Button>
          </form>
        </CardContent>
      </Card>
      <div className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>Emergency Contacts</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <form className="grid gap-3" onSubmit={(event) => void addContact(event)}>
              <Field name="name" label="Name" />
              <Field name="phone_number" label="Phone" />
              <Field name="relationship" label="Relationship" />
              <Button type="submit" disabled={createContact.isPending}>Add Contact</Button>
            </form>
            {(contacts.data ?? []).map((contact) => (
              <Row key={contact.id} title={contact.name} detail={`${contact.relationship} | ${contact.phone_number}`}>
                <Button size="icon" variant="ghost" onClick={() => void deleteContact.mutateAsync(contact.id)} aria-label="Delete contact">
                  <Trash2 className="h-4 w-4" aria-hidden="true" />
                </Button>
              </Row>
            ))}
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Dependents</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <form className="grid gap-3" onSubmit={(event) => void addDependent(event)}>
              <Field name="full_name" label="Full name" />
              <Field name="date_of_birth" label="Date of birth" type="date" />
              <Select name="gender" label="Gender" defaultValue="FEMALE">
                <option value="FEMALE">Female</option>
                <option value="MALE">Male</option>
                <option value="OTHER">Other</option>
              </Select>
              <Field name="relationship" label="Relationship" />
              <TextArea name="medical_notes" label="Medical notes" />
              <Button type="submit" disabled={createDependent.isPending}>Add Dependent</Button>
            </form>
            {(dependents.data ?? []).map((dependent) => (
              <Row key={dependent.id} title={dependent.full_name} detail={dependent.relationship}>
                <Button size="icon" variant="ghost" onClick={() => void deleteDependent.mutateAsync(dependent.id)} aria-label="Delete dependent">
                  <Trash2 className="h-4 w-4" aria-hidden="true" />
                </Button>
              </Row>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function NurseLifecyclePanel(): ReactNode {
  const profile = useNurseProfile();
  const updateProfile = useUpdateNurseProfile();
  const changeAvailability = useChangeAvailability();
  const geolocation = useGeolocation();
  const updateLocation = useUpdateLocation();
  const specializations = useSpecializations();
  const replaceSpecializations = useReplaceProfileSpecializations();
  const credentials = useCredentials();
  const uploadCredential = useUploadCredential();
  const availability = useAvailability();
  const createAvailability = useCreateAvailability();
  const deleteAvailability = useDeleteAvailability();
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function saveNurseProfile(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    const form = event.currentTarget;
    await updateProfile.mutateAsync({
      phone_number: formValue(form, "phone_number"),
      national_id: formValue(form, "national_id"),
      gender: formValue(form, "gender") as Gender,
      date_of_birth: formValue(form, "date_of_birth"),
      nck_license_number: formValue(form, "nck_license_number"),
      nck_license_expiry: formValue(form, "nck_license_expiry"),
      years_of_experience: Number(formValue(form, "years_of_experience") || 0),
      travel_radius_km: Number(formValue(form, "travel_radius_km") || 10),
      county: formValue(form, "county"),
      address: formValue(form, "address"),
      bio: formValue(form, "bio"),
    });
    setMessage("Nurse profile saved.");
  }

  async function setStatus(status: NurseStatus): Promise<void> {
    setMessage(null);
    setError(null);
    try {
      if (status === "ONLINE") {
        const coordinates = await geolocation.requestLocation();
        await updateLocation.mutateAsync(coordinates);
      }
      await changeAvailability.mutateAsync({
        status,
        location_visible: status === "ONLINE",
      });
      setMessage(status === "ONLINE" ? "Fresh GPS submitted and nurse is online." : `Status set to ${status}.`);
    } catch (requestError) {
      setError(getUserErrorMessage(requestError));
    }
  }

  async function upload(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    const form = event.currentTarget;
    const payload = new FormData(form);
    await uploadCredential.mutateAsync(payload);
    form.reset();
  }

  async function addAvailability(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    const form = event.currentTarget;
    await createAvailability.mutateAsync({
      day_of_week: Number(formValue(form, "day_of_week")),
      start_time: formValue(form, "start_time"),
      end_time: formValue(form, "end_time"),
    });
    form.reset();
  }

  async function saveSpecializations(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    const codes = Array.from(new FormData(event.currentTarget).getAll("specializations")).map(String);
    await replaceSpecializations.mutateAsync(codes);
  }

  if (profile.isLoading) return <LoadingState />;
  if (profile.error || !profile.data) return <ErrorState message="Nurse profile could not be loaded." />;

  const currentCodes = new Set(profile.data.specializations?.map((item) => item.code) ?? []);

  return (
    <div className="grid gap-4 xl:grid-cols-[minmax(0,1.1fr)_minmax(360px,0.9fr)]">
      <Card>
        <CardHeader>
          <CardTitle>Nurse Lifecycle</CardTitle>
        </CardHeader>
        <CardContent className="space-y-5">
          <div className="flex flex-wrap gap-2">
            <Badge variant="neutral">{profile.data.nck_verification_status}</Badge>
            <Badge variant="neutral">{profile.data.status}</Badge>
            <Badge variant={profile.data.is_available ? "success" : "neutral"}>
              {profile.data.is_available ? "Available" : "Unavailable"}
            </Badge>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button onClick={() => void setStatus("ONLINE")} disabled={changeAvailability.isPending || geolocation.loading}>
              <MapPin className="h-4 w-4" aria-hidden="true" />
              Go Online
            </Button>
            <Button variant="secondary" onClick={() => void setStatus("BUSY")}>
              <Clock className="h-4 w-4" aria-hidden="true" />
              Busy
            </Button>
            <Button variant="outline" onClick={() => void setStatus("OFFLINE")}>Offline</Button>
          </div>
          {message ? <p className="text-sm text-emerald-700">{message}</p> : null}
          {error ? <p className="text-sm text-destructive">{error}</p> : null}
          <form className="grid gap-4 md:grid-cols-2" onSubmit={(event) => void saveNurseProfile(event)}>
            <Field name="phone_number" label="Phone" defaultValue={profile.data.phone_number} />
            <Field name="national_id" label="National ID" defaultValue={profile.data.national_id} />
            <Select name="gender" label="Gender" defaultValue={profile.data.gender}>
              <option value="">Select gender</option>
              <option value="FEMALE">Female</option>
              <option value="MALE">Male</option>
              <option value="OTHER">Other</option>
            </Select>
            <Field name="date_of_birth" label="Date of birth" type="date" defaultValue={profile.data.date_of_birth} />
            <Field name="nck_license_number" label="NCK license" defaultValue={profile.data.nck_license_number} />
            <Field name="nck_license_expiry" label="NCK expiry" type="date" defaultValue={profile.data.nck_license_expiry} />
            <Field name="years_of_experience" label="Years of experience" type="number" defaultValue={profile.data.years_of_experience} />
            <Select name="travel_radius_km" label="Travel radius" defaultValue={String(profile.data.travel_radius_km ?? 10)}>
              <option value="10">10km</option>
              <option value="20">20km</option>
              <option value="50">50km</option>
              <option value="100">100km</option>
            </Select>
            <Field name="county" label="County" defaultValue={profile.data.county} />
            <TextArea name="address" label="Address" defaultValue={profile.data.address} />
            <div className="md:col-span-2">
              <TextArea name="bio" label="Bio" defaultValue={profile.data.bio} />
            </div>
            <Button className="md:col-span-2" type="submit" disabled={updateProfile.isPending}>
              <Save className="h-4 w-4" aria-hidden="true" />
              Save Nurse Profile
            </Button>
          </form>
        </CardContent>
      </Card>
      <div className="space-y-4">
        <Card>
          <CardHeader><CardTitle>Credentials</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <form className="grid gap-3" onSubmit={(event) => void upload(event)}>
              <Select name="credential_type" label="Credential type" defaultValue="NCK_LICENSE">
                <option value="NCK_LICENSE">NCK License</option>
                <option value="NATIONAL_ID">National ID</option>
                <option value="PASSPORT_PHOTO">Passport Photo</option>
                <option value="ACADEMIC_CERTIFICATE">Academic Certificate</option>
                <option value="PROFESSIONAL_CERTIFICATE">Professional Certificate</option>
              </Select>
              <Field name="image" label="Credential image" type="file" />
              <Button type="submit" disabled={uploadCredential.isPending}>
                <FileUp className="h-4 w-4" aria-hidden="true" />
                Upload
              </Button>
            </form>
            {(credentials.data ?? []).map((credential) => (
              <Row key={credential.id} title={credential.credential_type} detail={credential.verification_status} />
            ))}
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Specializations</CardTitle></CardHeader>
          <CardContent>
            <form className="grid gap-3" onSubmit={(event) => void saveSpecializations(event)}>
              {(specializations.data ?? []).map((item) => (
                <label key={item.code} className="flex items-center gap-2 text-sm">
                  <input name="specializations" type="checkbox" value={item.code} defaultChecked={currentCodes.has(item.code)} />
                  {item.name}
                </label>
              ))}
              <Button type="submit" disabled={replaceSpecializations.isPending}>
                <Check className="h-4 w-4" aria-hidden="true" />
                Save Specializations
              </Button>
            </form>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Availability</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <form className="grid gap-3" onSubmit={(event) => void addAvailability(event)}>
              <Select name="day_of_week" label="Day" defaultValue="1">
                <option value="1">Monday</option>
                <option value="2">Tuesday</option>
                <option value="3">Wednesday</option>
                <option value="4">Thursday</option>
                <option value="5">Friday</option>
                <option value="6">Saturday</option>
                <option value="7">Sunday</option>
              </Select>
              <Field name="start_time" label="Start" type="time" />
              <Field name="end_time" label="End" type="time" />
              <Button type="submit" disabled={createAvailability.isPending}>Add Shift</Button>
            </form>
            {(availability.data ?? []).map((slot) => (
              <Row key={slot.id} title={`Day ${slot.day_of_week}`} detail={`${slot.start_time} - ${slot.end_time}`}>
                <Button size="icon" variant="ghost" onClick={() => void deleteAvailability.mutateAsync(slot.id)} aria-label="Delete shift">
                  <Trash2 className="h-4 w-4" aria-hidden="true" />
                </Button>
              </Row>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function Field({
  defaultValue,
  label,
  name,
  type = "text",
}: {
  defaultValue?: string | number;
  label: string;
  name: string;
  type?: string;
}): ReactNode {
  return (
    <div className="space-y-2">
      <Label htmlFor={name}>{label}</Label>
      <Input id={name} name={name} type={type} defaultValue={defaultValue ?? ""} />
    </div>
  );
}

function Select({
  children,
  defaultValue,
  label,
  name,
}: {
  children: ReactNode;
  defaultValue?: string;
  label: string;
  name: string;
}): ReactNode {
  return (
    <div className="space-y-2">
      <Label htmlFor={name}>{label}</Label>
      <select id={name} name={name} defaultValue={defaultValue ?? ""} className={inputClass}>
        {children}
      </select>
    </div>
  );
}

function TextArea({
  defaultValue,
  label,
  name,
}: {
  defaultValue?: string;
  label: string;
  name: string;
}): ReactNode {
  return (
    <div className="space-y-2">
      <Label htmlFor={name}>{label}</Label>
      <textarea id={name} name={name} defaultValue={defaultValue ?? ""} className={textareaClass} />
    </div>
  );
}

function Row({
  children,
  detail,
  title,
}: {
  children?: ReactNode;
  detail: string;
  title: string;
}): ReactNode {
  return (
    <div className="flex min-h-14 items-center justify-between gap-3 rounded-md border border-border px-3 py-2">
      <div>
        <p className="text-sm font-medium">{title}</p>
        <p className="text-xs text-muted-foreground">{detail}</p>
      </div>
      {children}
    </div>
  );
}

export function ProfilePage(): ReactNode {
  const { user } = useAuth();

  return (
    <div className="space-y-6">
      <PageHeader
        title="Profile"
        description="Manage verification, availability, healthcare details, and protected contact data."
        actions={user ? <Badge variant="neutral">{user.role}</Badge> : null}
      />
      {user?.role === "PATIENT" ? <PatientProfilePanel /> : null}
      {user?.role === "NURSE" ? <NurseLifecyclePanel /> : null}
      {user?.role === "ADMIN" ? (
        <Card>
          <CardHeader><CardTitle>Administrator Profile</CardTitle></CardHeader>
          <CardContent className="grid gap-3 text-sm sm:grid-cols-2">
            <div><p className="text-muted-foreground">Email</p><p className="font-medium">{user.email}</p></div>
            <div><p className="text-muted-foreground">Role</p><Badge variant="neutral">{user.role}</Badge></div>
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}
